from flask import Flask, redirect, url_for, render_template, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
import os
from openai import OpenAI
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from pymongo import MongoClient
import random
from wordlist import words
import time
# from stockfish import Stockfish

   

genai.configure(api_key=os.getenv('GEMINIKEY'))

# stockfish_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stockfish')
# stockfish = Stockfish(path=stockfish_path)
openclient = OpenAI(api_key=os.getenv("OPENAIKEY"))
client = MongoClient(os.getenv('mongouri'))
db = client.db  # Replace 'your_database_name' with your database name
collection = db.data  # Replace 'your_collection_name' with your collection name

FILE_READ = False

class TrieNode:
    def __init__(self):
        self.parent = None
        self.children = {}
        self.is_end_of_word = False

    def add_word(self, word, index=0):
        if index == len(word):
            self.is_end_of_word = True
            self.word = word
            return
        ch = word[index]
        if ch not in self.children:
            self.children[ch] = TrieNode()
            self.children[ch].parent = self
        self.children[ch].add_word(word, index + 1)

CROSSWORD_LEN = len(words[0])
root = TrieNode()
for word in words:
    root.add_word(word)

def generate_all_words(required, curnode, allwords, index=0):
    if curnode.is_end_of_word:
        allwords.append(curnode.word)
        return
    requiredletters = required[index]
    for letter in curnode.children:
        if letter in requiredletters:
            generate_all_words(required, curnode.children[letter], allwords, index + 1)

def generate_crossword(crossword, trielist):
    if len(crossword) == CROSSWORD_LEN:
        if has_duplicate(crossword):
            return False
        return crossword
    required = [''.join(t.children.keys()) for t in trielist]
    matches = []
    generate_all_words(required, root, matches)
    random.shuffle(matches)
    for match in matches:
        crossword.append(match)
        for i, letter in enumerate(match):
            trielist[i] = trielist[i].children[letter]
        if generate_crossword(crossword, trielist):
            return crossword
        crossword.pop()
        for i, letter in enumerate(match):
            trielist[i] = trielist[i].parent
    return False

def has_duplicate(crossword):
    seen = set()
    for row in crossword:
        if row in seen:
            return True
        seen.add(row)
    for col in range(len(crossword[0])):
        s = ''.join(crossword[row][col] for row in range(len(crossword)))
        if s in seen:
            return True
        seen.add(s)
    return False

def crossword_gpt(prompt, model="gpt-4o-mini"):
    messages = [{
        "role": "system",
        "content": prompt
    }]

    chat = openclient.chat.completions.create(
        model=model,
        messages=messages
    )

    reply = chat.choices[0].message.content
    return reply



def gpt(message, mod, color, prev):
    messages = [{
        "role": "system",
        "content": f"It's your turn as {color}. (Previous Moves): {prev}, (FEN): {message}. "
                   f"Without giving explanations, please state the best 5 moves for {color}, each in a new line."
    }]

    chat = openclient.chat.completions.create(
        model="gpt-4o-mini",
        # model=mod,
        messages=messages
    )

    reply = chat.choices[0].message.content
    return reply

def gemini(message, color, prev):
    model = genai.GenerativeModel(model_name="gemini-2.5-flash-lite")
    
    response = model.generate_content([
        f"It's your turn as {color}. (Previous Moves): {prev}, (FEN): {message}. Without giving explanations, please state the best 5 moves for {color}, each in a new line."],
    safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    })


    print(response.text)
    return response.text


app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "whatsup3"
    #return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()

    mes = data.get('fen')
    mod = data.get('model')
    color = data.get('color')
    prev = data.get('prev')


    response = "Not a valid FEN"
    
    if (mes.count('/') >= 7):
        if (mod == 'gemini'):
            response = gemini(mes, color, prev)
        elif (mod == 'gpt-4o-mini'):
            response = gpt(mes, mod, color, prev)
        else:
            response = "Invalid model, only gemini and gpt-4o-mini accepted"

    return response, 200


@app.route('/data', methods=['GET'])
def get_data():
    return jsonify("hello")

@app.route('/gen2', methods=['GET'])
def get_data2():
    return jsonify("Hello")


@app.route('/insert', methods=['POST'])
def insert_data():
    try:
        data = request.get_json()
        insert_result = collection.insert_one(data)
        return jsonify({'message': 'Data inserted successfully', 'inserted_id': str(insert_result.inserted_id)}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route("/gen", methods=["GET"])
def generate():
    start = time.perf_counter()
    down_clues = {}
    across_clues = {}
    crossword = generate_crossword([], [root] * CROSSWORD_LEN)
    if not crossword:
        return jsonify({"error": "Failed to generate crossword"}), 500

    prompt_string = f"Generate a creative, clever crossword clue for the following words. For formatting, put each clue question in a new line. There should be {len(crossword) * 2} lines. Label them with their clue number : then a space, like 1: 2:. Do not say the clue. Your response must only contain clue questions. The first line should just be the first clue question. Avoid punctuation. Here is the word list:\n"
    for col in range(len(crossword)):
        s = ''.join(crossword[row][col] for row in range(len(crossword)))
        prompt_string += s + "\n"
    for row in crossword:
        prompt_string += row + "\n"

    prompt_response = crossword_gpt(prompt_string)

    linenum = 0
    for i, line in enumerate(prompt_response.splitlines()):
        if line.strip() == "":
            continue
        if ':' in line:
            key, value = line.split(':', 1)
            if linenum < len(crossword):
                down_clues[linenum + 1] = value.strip()
            elif linenum == len(crossword):
                across_clues[1] = value.strip()
            else:
                across_clues[linenum] = value.strip()
        linenum += 1

    final_dict = {
        "title": "AI Generated Mini Crossword",
        "solution": crossword,
        "across": across_clues,
        "down": down_clues,
        "message": "Good job!"
    }
    end = time.perf_counter()
    final_dict["execution_time_sec"] = round(end - start, 3)
    return jsonify(final_dict)


if __name__ == "__main__":
    app.run(port=5002, debug=True)