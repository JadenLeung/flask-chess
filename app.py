from flask import Flask, redirect, url_for, render_template, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
import os
import openai
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from pymongo import MongoClient
from stockfish import Stockfish

   
openai.api_key = os.getenv('OPENAIKEY')
genai.configure(api_key=os.getenv('GEMINIKEY'))

# stockfish_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stockfish')
# stockfish = Stockfish(path=stockfish_path)

client = MongoClient(os.getenv('mongouri'))
db = client.db  # Replace 'your_database_name' with your database name
collection = db.data  # Replace 'your_collection_name' with your collection name


def gpt(message, mod, color, prev):
    messages = [ {"role": "system", "content":  
                f"It's your turn as {color}. (Previous Moves): {prev}, (FEN): {message}. Without giving explanations, please state the best 5 moves for {color}, each in a new line."} ] 

    chat = openai.ChatCompletion.create( 
       # model="gpt-4o-mini", messages=messages
        model = mod, messages = messages
    ) 
    reply = chat.choices[0].message.content 
    return reply

def gemini(message, color, prev):
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")
    
    response = model.generate_content([
        f"It's your turn as {color}. (Previous Moves): {prev}, (FEN): {message}. Without giving explanations, please state the best 5 moves for {color}, each in a new line."],
    safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    })


    print(response.text)
    return response.text

def deepseek(message, mod, color, prev):
    client = openai(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv('DEEPSEEKKEY'),
    )

    completion = client.chat.completions.create(
    extra_headers={
        "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
        "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
    },
    model="deepseek/deepseek-r1:free",
    messages=[
        {
            "role": "user",
            "content": f"It's your turn as {color}. (Previous Moves): {prev}, (FEN): {message}. Without giving explanations, please state the best 5 moves for {color}, each in a new line."
        }
    ])
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "whatsup2"
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
        elif (mod == 'deepseek'):
            response = deepseek(mes, color, prev)
        elif (mod == 'gpt-4o-mini'):
            response = gpt(mes, mod, color, prev)
        else:
            response = "Invalid model, only gemini and gpt-4o-mini accepted"

    return response, 200


@app.route('/data', methods=['GET'])
def get_data():
    data = list(collection.find({}, {'_id': 0}))  # Exclude '_id' from the result
    return jsonify(data)


@app.route('/insert', methods=['POST'])
def insert_data():
    try:
        data = request.get_json()
        insert_result = collection.insert_one(data)
        return jsonify({'message': 'Data inserted successfully', 'inserted_id': str(insert_result.inserted_id)}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    


if __name__ == "__main__":
    app.run(port=5002, debug=True)

#python3 -m pip freeze > requirements.txt