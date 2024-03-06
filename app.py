from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import threading
app = Flask(__name__)
CORS(app, resources={r"/process": {"origins": ["https://genai-main-poc.web.app/", "http://localhost:3000/"]}})
CORS(app, resources={r"/process": {"origins": "*"}})
CORS(app, resources={r"/get_welcome_message": {"origins": ["https://genai-main-poc.web.app/", "http://localhost:3000/"]}})
CORS(app, resources={r"/get_welcome_message": {"origins": "*"}})

chatgpt_url = "http://34.93.3.215:8000/chat_conversation"
user_conversations = {}
conversation_locks = {}

def get_chatgpt_completion(conversation):
    response = requests.post(chatgpt_url, json=conversation, timeout=10)
    return response.json()

def create_new_conversation(user_id):
    user_conversations[user_id] = []
    conversation_locks[user_id] = threading.Lock()

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
    user_id = request.json.get('session_id')
    user_input = request.json.get('user_input')

    # Check if the user has an existing conversation
    if user_id not in user_conversations:
        with conversation_locks.setdefault(user_id, threading.Lock()):
            create_new_conversation(user_id)

    with conversation_locks[user_id]:
        # Check if the user input is the completion trigger
        if user_input.strip().lower() == "i have completed viewing the video":
            response = "Great! If you have any more questions in the future, feel free to ask."
            user_conversations[user_id] = []  # Start a new conversation
        else:
            api_response = requests.get('http://34.93.3.215:8000/welcome_message')
            data = api_response.json()
            response = data['conversation'][0]['message']
            user_conversations[user_id].append({"role": "assistant", "content": response})

            # Add user message to the current conversation
            user_conversations[user_id].append({"role": "user", "content": user_input})
            chatgpt_request = {'user_message': user_input, 'conversation_history': user_conversations[user_id]}
            chatgpt_response = get_chatgpt_completion(chatgpt_request)
            response = chatgpt_response
            user_conversations[user_id].append({"role": "assistant", "content": response})

    print(response)
    print("Conversation History: ")
    print(user_conversations)
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
