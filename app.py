from flask import Flask, request
import google.generativeai as genai

app = Flask(__name__)
model_name = "models/gemini-1.5-flash"  # Add the correct prefix
chat_session = genai.ChatSession(model=model_name)  # Using the correct model name

def generate():
    # Get user input from the JSON body
    print('got the request')
    data = request.get_json()

    # Ensure 'description' key exists in the JSON request
    if 'description' not in data:
        return {"error": "Description is required"}, 400

    user_input = data['description']

    # Call the send_message method to generate content
    try:
        response = chat_session.send_message(user_input)
        
        # Check if response is valid and return the output
        if response and 'output' in response:
            return {"output": response['output']}
        else:
            return {"error": "Failed to generate response"}, 500

    except Exception as e:
        return {"error": str(e)}, 500  # Catch and return any exceptions

if __name__ == '__main__':
    generate()
