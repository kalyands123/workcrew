from flask import Flask, request
import google.generativeai as genai

# Initialize the Flask app
app = Flask(__name__)

# Configure the Generative AI API key
api_key = "AIzaSyCm8A-ip22RQQA4Cabq8_oNIXuQnZjAbGU"
genai.configure(api_key=api_key)

# Get the correct model object
model_name = "models/gemini-1.5-flash"
model = genai.get_model(model_name)  # Fetch the model object using get_model

# Create a chat session with the fetched model
chat_session = genai.ChatSession(model=model)

# Define the route for generating responses
@app.route('/generate', methods=['POST'])
def generate():
    # Get user input from the JSON body
    print('Got the request')
    data = request.get_json()

    # Ensure 'description' key exists in the JSON request
    if 'description' not in data:
        return {"error": "Description is required"}, 400

    user_input = data['description']

    # Call the send_message method to generate content
    try:
        response = chat_session.send_message(user_input)

        # Check if response is valid and return the output
        if response and response.last:
            return {"output": response.last['content']}
        else:
            return {"error": "Failed to generate response"}, 500

    except Exception as e:
        return {"error": str(e)}, 500  # Catch and return any exceptions

# Start the Flask application
if __name__ == '__main__':
    app.run(debug=True)
