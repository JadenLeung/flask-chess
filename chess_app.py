from flask import Blueprint, request, jsonify
import os
from openai import OpenAI
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from pymongo import MongoClient

genai.configure(api_key=os.getenv('GEMINIKEY'))
openclient = OpenAI(api_key=os.getenv("OPENAIKEY"))
client = MongoClient(os.getenv('mongouri'))
db = client.db
collection = db.data

chess_bp = Blueprint('chess', __name__)

def gpt(message, mod, color, prev):
    messages = [{
        "role": "system",
        "content": f"It's your turn as {color}. (Previous Moves): {prev}, (FEN): {message}. "
                   f"Without giving explanations, please state the best 5 moves for {color}, each in a new line."
    }]

    chat = openclient.chat.completions.create(
        model="gpt-4o-mini",
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

    return response.text

@chess_bp.route('/submit', methods=['POST'])
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

@chess_bp.route('/data', methods=['GET'])
def get_data():
    return jsonify("hello")

@chess_bp.route('/gen2', methods=['GET'])
def get_data2():
    return jsonify("Hello")

@chess_bp.route('/insert', methods=['POST'])
def insert_data():
    try:
        data = request.get_json()
        insert_result = collection.insert_one(data)
        return jsonify({'message': 'Data inserted successfully', 'inserted_id': str(insert_result.inserted_id)}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
