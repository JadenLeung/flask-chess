from flask import Flask, redirect, url_for, render_template, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
import os
import openai
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

   
openai.api_key = os.getenv('OPENAIKEY')
genai.configure(api_key=os.getenv('GEMINIKEY'))


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
    return "whatsup1"
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


if __name__ == "__main__":
    app.run(port=5002, debug=True)

#python3 -m pip freeze > requirements.txt