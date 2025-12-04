from flask import Flask
from flask_cors import CORS
from chess_app import chess_bp
from crossword_app import crossword_bp

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(chess_bp)
app.register_blueprint(crossword_bp)

@app.route('/')
def home():
    return "whatsup4"

if __name__ == "__main__":
    app.run(port=5002, debug=True)