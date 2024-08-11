from flask import Flask, redirect, url_for, render_template, request, jsonify
from dotenv import load_dotenv
import os
import openai

openai.api_key = os.getenv('OPENAIKEY')

def gpt(message, mod):
    messages = [ {"role": "system", "content":  
                # f"It's your turn as black. Which move will come next? (FEN): {message}'. Answer strictly in the form [Piece name]: [Old square]->[New square]"} ] 
                message} ] 

    chat = openai.ChatCompletion.create( 
       # model="gpt-4o-mini", messages=messages
        model = mod, messages = messages
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
    mod = data.get('model')

    gptresponse = "Not a valid FEN"
    
    if (mes.count('/') >= 7):
        gptresponse = gpt(mes, mod)

    return gptresponse, 200


if __name__ == "__main__":
    app.run(port=5002, debug=True)

#python3 -m pip freeze > requirements.txt