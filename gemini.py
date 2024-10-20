import google.generativeai as genai
from flask import Flask, request, jsonify

# Configure the API key
api_key = "AIzaSyCm8A-ip22RQQA4Cabq8_oNIXuQnZjAbGU"
genai.configure(api_key=api_key)

# Initialize Flask app
app = Flask(__name__)

# Define the route for POST requests
@app.route('/generate-description', methods=['POST'])
def generate_description():
    try:
        # Get the description from the request's JSON data
        data = request.get_json()
        description = data.get('description')
        
        if not description:
            return jsonify({"error": "No description provided"}), 400
        
        # Initialize the generative model
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Generate content based on the input description
        response = model.generate_content(description)
        
        # Return the generated content as a response
        return jsonify({"generated_content": response.text}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
