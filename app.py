from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, resources={r"/process": {"origins": ["https://genai-main-poc.web.app/", "http://localhost:3000/"]}})
CORS(app, resources={r"/process": {"origins": "*"}})
CORS(app, resources={r"/get_welcome_message": {"origins": ["https://genai-main-poc.web.app/", "http://localhost:3000/"]}})
CORS(app, resources={r"/get_welcome_message": {"origins": "*"}})

chatgpt_url = "http://34.93.3.215:8000/chat_conversation"
user_sessions = {}

def get_chatgpt_completion(conversation):
    response = requests.post(chatgpt_url, json=conversation, timeout=10)
    return response.json()

@app.route('/get_welcome_message', methods=['GET'])
def get_welcome_message():
    try:
        api_response = requests.get('http://34.93.3.215:8000/welcome_message')
        data = api_response.json()
        return jsonify(data)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/process', methods=['POST'])
def process():
    user_input = request.json.get('user_input')
    user_ip = request.remote_addr  # Get user's IP address as a simple session identifier

    if user_ip not in user_sessions:
        user_sessions[user_ip] = []  # Create a new conversation history for the user

    # Check if the user input is the completion trigger
    if user_input.strip().lower() == "i have completed viewing the video":
        response = "Great! If you have any more questions in the future, feel free to ask."
        user_sessions[user_ip].append({"role": "user", "content": user_input})
        user_sessions[user_ip].append({"role": "assistant", "content": response})
    else:
        api_response = requests.get('http://34.93.3.215:8000/welcome_message')
        data = api_response.json()
        response = data['conversation'][0]['message']
        user_sessions[user_ip].append({"role": "assistant", "content": response})
        user_sessions[user_ip].append({"role": "user", "content": user_input})
        chatgpt_request = {'user_message': user_input, 'conversation_history': user_sessions[user_ip]}
        chatgpt_response = get_chatgpt_completion(chatgpt_request)
        response = chatgpt_response
        user_sessions[user_ip].append({"role": "assistant", "content": response})

    print(response)
    print("Conversation History: ")
    print(user_sessions[user_ip])
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
