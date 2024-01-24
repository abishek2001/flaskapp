from flask import Flask, request, jsonify,  redirect
from flask_cors import CORS
import requests  # Import requests library

app = Flask(__name__)
CORS(app, resources={r"/process": {"origins": "*"}})


# Define the endpoint URL and headers for the ChatGPT model
chatgpt_url = "https://courseadminbot.azurewebsites.net/botReplyGenerate"
chatgpt_headers = {
    "Content-Type": "application/json",
    "x-functions-key": "q0j51tgxCOqqg2sBLyTV41CeTxKt5hmCh1lqSAxb7IEDAzFu7gRl3g=="
}

# Initialize conversation history as an empty list
conversation_history = []

def get_chatgpt_completion(conversation):
    response = requests.post(chatgpt_url, json=conversation, headers=chatgpt_headers)
    return response.json()

@app.route('/process', methods=['POST'])
def process():
    user_input = "hi"
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
        chatgpt_request = {'course_structure': {'skill': 'Business Communication', 'topics': ["Introduction to business communication","Basic communication principles","Effective verbal communication","Active listening skills","Written communication skills","Non-verbal communication","Professional email etiquette"]},
                           'conv_history': conversation_history}
        chatgpt_response = get_chatgpt_completion(chatgpt_request)
        response = chatgpt_response.get("message")
        function_call = chatgpt_response.get("function_call")

        # Check if a function call is received, and perform redirection
        if function_call:
            response ="Redirect"
            conversation_history.append([])
        # Add chatbot message to the current conversation
        conversation_history[-1].append({"role": "assistant", "content": response})

    print(response)
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
