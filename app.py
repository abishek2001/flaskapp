from flask import Flask, request, jsonify,  redirect, session
from flask_cors import CORS
import requests  # Import requests library
import uuid
app = Flask(__name__)
app.secret_key = "disprz123"
CORS(app, resources={r"/process": {"origins": ["https://genai-main-poc.web.app/", "http://localhost:3000/"]}})
CORS(app, resources={r"/process": {"origins": "*"}})
CORS(app, resources={r"/get_welcome_message": {"origins": ["https://genai-main-poc.web.app/", "http://localhost:3000/"]}})
CORS(app, resources={r"/get_welcome_message": {"origins": "*"}})
# Define the endpoint URL and headers for the ChatGPT model
chatgpt_url = "http://34.93.3.215:8000/chat_conversation"
sessions = {}
# chatgpt_headers = {
#     "Content-Type": "application/json",
#     "x-functions-key": "q0j51tgxCOqqg2sBLyTV41CeTxKt5hmCh1lqSAxb7IEDAzFu7gRl3g=="
# }
# Initialize conversation history as an empty list
conversation_history = []
# endpoint_url = "http://34.93.3.215:8000/"
# response = requests.get(endpoint_url)
# endpoint_message = response.json()
# conversation_history.append([]) 
# conversation_history[-1].append({"role": "assistant", "content": endpoint_message})
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
    session_id = request.json.get('session_id')

    if not session_id or session_id not in sessions:
        # If no session ID or session not found, create a new session
        session_id = str(uuid.uuid4())
        sessions[session_id] = []

    if user_input.strip().lower() == "i have completed viewing the video":
        # Reset conversation history when the user completes viewing the video
        response = "Great! If you have any more questions in the future, feel free to ask."
        sessions[session_id] = []

    else:
        # Continue the conversation
        api_response = requests.get('http://34.93.3.215:8000/welcome_message')
        data = api_response.json()
        response = data['conversation'][0]['message']
        sessions[session_id].append({"role": "assistant", "content": response})
        sessions[session_id].append({"role": "user", "content": user_input})
        chatgpt_request = {'user_message': user_input, 'conversation_history': sessions[session_id]}
        chatgpt_response = get_chatgpt_completion(chatgpt_request)
        response = chatgpt_response

    print(response)
    print("Conversation History: ")
    print(sessions[session_id])

    # Include the session ID in the response
    return jsonify({"response": response, "session_id": session_id})

if __name__ == '__main__':
    app.run(debug=True)
