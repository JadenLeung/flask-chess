from flask import Flask, redirect, url_for, render_template, request, jsonify
from dotenv import load_dotenv
import os
import openai

openai.api_key = os.getenv('OPENAIKEY')

def gpt(message):
    '''returns a list of potential diseases from the GPT model'''
    messages = [ {"role": "system", "content":  
                f" You are a very strong chess engine. The chess board is in the following state (FEN): '{message}'. What is the best move for black? Answer strictly in the form [Piece name]: [Old square]->[New square]"} ] 


    chat = openai.ChatCompletion.create( 
        model="gpt-4o-mini", messages=messages 
    ) 
    reply = chat.choices[0].message.content 
    return reply

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello world: 6"
    #return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()

    mes = data.get('message')

    gptresponse = "Not a valid FEN"
    
    if (mes.count('/') >= 7):
        gptresponse = gpt(mes)

    return gptresponse, 200


if __name__ == "__main__":
    app.run(port=5002, debug=True)

#python3 -m pip freeze > requirements.txt