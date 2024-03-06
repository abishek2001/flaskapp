from flask import Flask, request, jsonify, session
from flask_cors import CORS
import requests

app = Flask(__name__)
app.secret_key = "disprz"  # Change this to a random secret key
CORS(app, resources={r"/process": {"origins": ["https://genai-main-poc.web.app/", "http://localhost:3000/"]}})
CORS(app, resources={r"/process": {"origins": "*"}})
CORS(app, resources={r"/get_welcome_message": {"origins": ["https://genai-main-poc.web.app/", "http://localhost:3000/"]}})
CORS(app, resources={r"/get_welcome_message": {"origins": "*"}})

chatgpt_url = "http://34.93.3.215:8000/chat_conversation"

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

    # Check if the user input is the completion trigger
    if user_input.strip().lower() == "i have completed viewing the video":
        response = "Great! If you have any more questions in the future, feel free to ask."
        session.pop('conversation_history', None)  # Reset the conversation history for the current user
    else:
        # Initialize conversation history for the current user if not present
        conversation_history = session.get('conversation_history', [])
        
        api_response = requests.get('http://34.93.3.215:8000/welcome_message')
        data = api_response.json()
        response = data['conversation'][0]['message']
        conversation_history.append({"role": "assistant", "content": response})
        
        # Add user message to the current conversation
        conversation_history.append({"role": "user", "content": user_input})
        chatgpt_request = {'user_message': user_input, 'conversation_history': conversation_history}
        chatgpt_response = get_chatgpt_completion(chatgpt_request)
        response = chatgpt_response

        # Update the session variable with the modified conversation history
        session['conversation_history'] = conversation_history

    print("Conversation History: ")
    print(session.get('conversation_history', []))

    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
