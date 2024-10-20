import json
import os
import pandas as pd  # Pandas to handle CSV and Excel files
from flask import Flask, jsonify, request

app = Flask(__name__)

# Load JSON data from an uploaded file
def load_json_data_from_file(uploaded_file):
    try:
        raw_data = uploaded_file.read().decode('utf-8')  # Read and decode the file content
        # Handle cases where multiple JSON objects are separated by new lines
        data = [json.loads(line) for line in raw_data.splitlines() if line.strip()]
        return data
    except json.JSONDecodeError as e:
        return {"error": f"JSON Decode Error: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}

# Load CSV data from an uploaded file
def load_csv_data_from_file(uploaded_file):
    try:
        # Read the CSV file into a DataFrame and convert it to a list of dictionaries
        df = pd.read_csv(uploaded_file)
        return df.to_dict(orient='records')
    except Exception as e:
        return {"error": f"CSV Read Error: {str(e)}"}

# Load Excel data from an uploaded file
def load_excel_data_from_file(uploaded_file):
    try:
        # Read the Excel file into a DataFrame and convert it to a list of dictionaries
        df = pd.read_excel(uploaded_file)
        return df.to_dict(orient='records')
    except Exception as e:
        return {"error": f"Excel Read Error: {str(e)}"}

# Define a route to accept file uploads and process them
@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Check if a file is part of the request
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
        
        uploaded_file = request.files['file']
        
        # Check if the file has a valid filename
        if uploaded_file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Determine the file type based on the extension
        file_extension = uploaded_file.filename.split('.')[-1].lower()

        # Load data from the file based on its type
        if file_extension == 'json':
            incoming_data = load_json_data_from_file(uploaded_file)
        elif file_extension == 'csv':
            incoming_data = load_csv_data_from_file(uploaded_file)
        elif file_extension in ['xls', 'xlsx']:
            incoming_data = load_excel_data_from_file(uploaded_file)
        else:
            return jsonify({"error": "Unsupported file type. Only JSON, CSV, and Excel files are allowed."}), 400

        if isinstance(incoming_data, dict) and "error" in incoming_data:
            return jsonify(incoming_data), 400  # Return error if loading failed

        # Print incoming_data to console (can be viewed in terminal logs)
        print("Incoming Data:", incoming_data)

        # Define the directory and filename to save the processed data
        save_directory = r"C:\Users\91901\OneDrive\Desktop\Saved"
        save_file_path = os.path.join(save_directory, f"Upload_Data.json")

        # Create the directory if it doesn't exist
        os.makedirs(save_directory, exist_ok=True)

        # Open the file in append mode and save the data as JSON
        with open(save_file_path, 'a') as f:
            json.dump(incoming_data, f, indent=4)  # Save the data in JSON format
            f.write('\n')  # Add a newline for each entry

        # Return both the success message and the processed incoming data
        return jsonify({
            "message": "Data successfully saved in JSON format",
            "file": save_file_path,
            "incoming_data": incoming_data  # Include incoming_data in the response
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
