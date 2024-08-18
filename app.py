from flask import Flask, redirect, url_for, render_template, request, jsonify
from dotenv import load_dotenv
import os
import openai
import google.generativeai as genai


openai.api_key = os.getenv('OPENAIKEY')
genai.configure(api_key=os.getenv('GEMINIKEY'))

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

def gemini(message):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content([message])
    print(response.text)
    return response.text



app = Flask(__name__)

@app.route('/')
def home():
    return "Hello world: 7"
    #return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()

    mes = data.get('message')
    mod = data.get('model')

    response = "Not a valid FEN"
    
    if (mes.count('/') >= 7):
        if (mod == 'gemini'):
            response = gemini(mes)
        else:
            response = gpt(mes, mod)

    return response, 200


if __name__ == "__main__":
    app.run(port=5002, debug=True)

#python3 -m pip freeze > requirements.txt