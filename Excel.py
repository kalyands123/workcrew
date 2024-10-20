import pandas as pd
from flask import Flask, jsonify

app = Flask(__name__)

# Load data from the Excel file
def load_excel_data(file_path):
    try:
        # Load the Excel file into a DataFrame
        df = pd.read_excel(file_path)
        # Convert DataFrame to a dictionary
        data = df.to_dict(orient='records')
        return data
    except Exception as e:
        # General error handling
        return {"error": str(e)}

# Path to your Excel file
excel_file_path = r"C:\Users\91901\OneDrive\Desktop\Excel data\Jodo Outplacement List.xlsx"

# Load data
data = load_excel_data(excel_file_path)

# Define a route to return the data
@app.route('/data', methods=['GET'])
def get_data():
    # Return the loaded data or an error message
    if isinstance(data, list) or isinstance(data, dict):
        return jsonify(data)
    else:
        return jsonify({"error": "Failed to load data"})

if __name__ == '__main__':
    app.run(debug=True)
