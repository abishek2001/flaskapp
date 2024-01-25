from flask import Flask, request, jsonify,  redirect
from flask_cors import CORS
import requests  # Import requests library

app = Flask(__name__)
CORS(app, resources={r"/process": {"origins": ["https://genai-main-poc.web.app/", "http://localhost:3000/"]}})
CORS(app, resources={r"/process": {"origins": "*"}})


# Define the endpoint URL and headers for the ChatGPT model
chatgpt_url = "http://35.200.210.182:8000/chat_conversation"
# chatgpt_headers = {
#     "Content-Type": "application/json",
#     "x-functions-key": "q0j51tgxCOqqg2sBLyTV41CeTxKt5hmCh1lqSAxb7IEDAzFu7gRl3g=="
# }
# Initialize conversation history as an empty list
conversation_history = []
def get_chatgpt_completion(conversation):
    response = requests.post(chatgpt_url, json=conversation, timeout=10)
    return response.json()
@app.route('/process', methods=['POST'])
def process():
    user_input = request.json.get('user_input')
    # Check if the user input is the completion trigger
    if user_input.strip().lower() == "i have completed viewing the video":
        response = "Great! If you have any more questions in the future, feel free to ask."
        conversation_history.append([])  # Start a new conversation
        conversation_history[-1].append({"role": "user", "content": user_input})
        conversation_history[-1].append({"role": "assistant", "content": response})
    else:
        if not conversation_history:
            conversation_history.append([])  # Start a new conversation if there's none
        # Add user message to the current conversation
        conversation_history[-1].append({"role": "user", "content": user_input})
        # Get chatbot response based on the entire conversation history
        chatgpt_request = {'user_input': user_input,
                            'login_id': 56,
                            'role': "Customer Expert Specialist",
                            'proficiency_level': "Beginner",
                            'language': "English",
                            'geography': "India"}
        chatgpt_response = get_chatgpt_completion(chatgpt_request)
        response = chatgpt_response
        # function_call = chatgpt_response.get("function_call")
        # # Check if a function call is received, and perform redirection
        # if function_call:
        #     response ="Redirect"
        #     conversation_history.append([])
        # Add chatbot message to the current conversation
        conversation_history[-1].append({"role": "assistant", "content": response})
    print(response)
    return jsonify({"response": response})
if __name__ == '__main__':
    app.run(debug=True)
