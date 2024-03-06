from flask import Flask, request, jsonify,  redirect, session
from flask_cors import CORS
import requests  # Import requests library
app = Flask(__name__)
app.secret_key = "disprz123"
CORS(app, resources={r"/process": {"origins": ["https://genai-main-poc.web.app/", "http://localhost:3000/"]}})
CORS(app, resources={r"/process": {"origins": "*"}})
CORS(app, resources={r"/get_welcome_message": {"origins": ["https://genai-main-poc.web.app/", "http://localhost:3000/"]}})
CORS(app, resources={r"/get_welcome_message": {"origins": "*"}})
# Define the endpoint URL and headers for the ChatGPT model
chatgpt_url = "http://34.93.3.215:8000/chat_conversation"
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
    # Check if the user input is the completion trigger
    if user_input.strip().lower() == "i have completed viewing the video":
        response = "Great! If you have any more questions in the future, feel free to ask."
        session['conversation_history'] = []  # Start a new conversation
        session['conversation_history'].append({"role": "user", "content": user_input})
        session['conversation_history'].append({"role": "assistant", "content": response})
    else:
        if 'conversation_history' not in session:
            session['conversation_history'] = []  # Start a new conversation if there's none

        api_response = requests.get('http://34.93.3.215:8000/welcome_message')
        data = api_response.json()
        response = data['conversation'][0]['message']

        session['conversation_history'].append({"role": "assistant", "content": response})
        session['conversation_history'].append({"role": "user", "content": user_input})

        chatgpt_request = {'user_message': user_input, 'conversation_history': session['conversation_history']}
        chatgpt_response = get_chatgpt_completion(chatgpt_request)
        response = chatgpt_response

        session['conversation_history'].append({"role": "assistant", "content": response})

    print(response)
    print("Conversation History: ")
    print(session['conversation_history'])
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
