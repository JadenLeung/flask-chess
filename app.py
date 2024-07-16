from flask import Flask, redirect, url_for, render_template, request, jsonify
import openai

openai.api_key = 'sk-proj-FVrKmdgT7dHBaSblfxeIT3BlbkFJpJx9sq39TFDbqT6pJP2j'

def gpt(message):
    '''returns a list of potential diseases from the GPT model'''
    messages = [ {"role": "system", "content":  
                message} ] 


    chat = openai.ChatCompletion.create( 
        model="gpt-3.5-turbo", messages=messages 
    ) 
    reply = chat.choices[0].message.content 
    return reply

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello world: 1"
    #return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()

    mes = data.get('message')
    
    gptresponse = gpt(mes)

    return jsonify(message=gptresponse), 200


if __name__ == "__main__":
    app.run(port=5002, debug=True)

#python3 -m pip freeze > requirements.txt