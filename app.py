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

stockfish_path = os.path.join(os.path.dirname(__file__), 'stockfish')
stockfish = Stockfish(path=stockfish_path)

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
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    
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
        elif (mod == 'gpt-4o-mini'):
            response = gpt(mes, mod, color, prev)
        else:
            response = "Invalid model, only gemini and gpt-4o-mini accepted"

    return response, 200


@app.route('/data', methods=['GET'])
def get_data():
    data = list(collection.find({}, {'_id': 0}))  # Exclude '_id' from the result
    return jsonify(data)

@app.route('/move', methods=['GET'])
def get_best_move():
    fen = request.args.get('fen')
    time = request.args.get('time')
    if fen:
        stockfish.set_fen_position(fen)
        best_move = stockfish.get_best_move_time(time)
        return jsonify({
            'best_move': best_move
        })
    return jsonify({'error': 'FEN parameter is required'}), 400

@app.route('/eval', methods=['GET'])
def get_eval_move():
    fen = request.args.get('fen')
    if fen:
        stockfish.set_fen_position(fen)
        evaluation = stockfish.get_evaluation()  # Get the evaluation score
        evaluation_pawns = evaluation['value'] / 100 if evaluation['type'] == 'cp' else evaluation['value']
        return jsonify({
            'evaluation': {
                'type': evaluation['type'],
                'value': evaluation_pawns
            }
        })
    return jsonify({'error': 'FEN parameter is required'}), 400




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