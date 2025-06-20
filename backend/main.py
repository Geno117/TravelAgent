from flask import Flask, request, jsonify
from flask_cors import CORS

from chat_assistant import LLM  

app = Flask(__name__)

# Enable CORS for all routes
CORS(app, origins=['http://localhost:5173', 'http://localhost:3000'])

llm = LLM()

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        
        # For now, just echo back the message
        # You can replace this with your LLM logic later
        response = llm.generate_response(message)
        
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5001)