import json
import os
import pandas 
from flask import Flask, jsonify, request

app = Flask(__name__)

# Load JSON data from the file
def load_json_data(file_path):
    try:
        with open(file_path, 'r') as f:
            raw_data = f.read()
            # Handle cases where multiple JSON objects are separated by new lines
            data = [json.loads(line) for line in raw_data.splitlines() if line.strip()]
        return data
    except json.JSONDecodeError as e:
        return {"error": f"JSON Decode Error: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}

# Path to your JSON file
json_file_path = r"C:\Users\91901\Downloads\Zest_Employee_Details.json"

# Load data
data = load_json_data(json_file_path)

# Define a route to return the data (GET request)
@app.route('/data', methods=['GET'])
def get_data():
    if isinstance(data, list) or isinstance(data, dict):
        return jsonify(data)
    else:
        return jsonify({"error": "Failed to load JSON data"})

# Define a route to accept POST data and save it to the file (POST request)
@app.route('/save-data', methods=['POST'])
def save_data():
    try:
        # Get the JSON data from the request
        incoming_data = request.get_json()

        if incoming_data is None:
            return jsonify({"error": "No JSON data provided"}), 400

        # Define the directory and filename to save the JSON
        save_directory = r"C:\Users\91901\OneDrive\Desktop\Saved"
        save_file_path = os.path.join(save_directory, "Saved_Employee_Data.json")

        # Create the directory if it doesn't exist
        os.makedirs(save_directory, exist_ok=True)

        # Open the file in append mode and write the new data
        with open(save_file_path, 'a') as f:
            f.write(json.dumps(incoming_data) + '\n')

        return jsonify({"message": "Data successfully saved", "file": save_file_path})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
