<h3>API Overview</h3>

Use this API to play Gemini or GPT-4o-mini in chess! The LLM will display the best 5 moves in the position. Not all these moves may be valid.

<h4>API usage</h4>
This API is used in my game where you can pit the 2 LLMs against each other. Check it out: https://jadenleung.github.io/#/aichess

<h4>Endpoint</h4> https://monkey2.azurewebsites.net/submit
<h4>Parameters</h4>

```fen```: The FEN (Forsyth-Edwards Notation) representation of the current game position.

```prev```: The previous moves played, e.g. "1. e4 e5 2. f4 exf4"

```color```: The color the bot represents (white/black)

```model```: Either "gpt-4o-mini" or "gemini"

<h4>Example API call</h4>

curl --insecure --location --request POST 'https://monkey2.azurewebsites.net/submit' --header 'Content-Type: application/json' --data-raw '{"fen":"rnbqkbnr/pppp1ppp/8/4p3/3PP3/8/PPP2PPP/RNBQKBNR","model":"gemini","color":"black","prev":"1. e4 e5 2. d4"}'

<h4>Example API response</h4>

Nf6 <br/>
Nc6 <br/>
exd4 <br/>
Be7 <br/>
d5 <br/>

<h4>Prompt given to LLM</h4>
"It's your turn as {color}. Previous Moves: {prev}, FEN: {fen}. Without giving explanations, please state the best 5 moves for {color}, each in a new line."
