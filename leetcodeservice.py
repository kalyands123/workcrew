from flask import Flask, jsonify, request
import requests
import json

app = Flask(__name__)

# Function to get LeetCode user data via GraphQL
def get_leetcode_graphql_data(username):
    url = 'https://leetcode.com/graphql'
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # GraphQL query to fetch user data
    query = f'''
    {{
        matchedUser(username: "{username}") {{
            username
            profile {{
                realName
                reputation
                ranking
                countryName
            }}
            submitStats {{
                acSubmissionNum {{
                    difficulty
                    count
                }}
                totalSubmissionNum {{
                    count
                }}
            }}
        }}
    }}
    '''

    response = requests.post(url, json={'query': query}, headers=headers)

    if response.status_code != 200:
        return {"error": f"HTTP Error {response.status_code} for user {username}"}, response.status_code

    data = response.json()

    if 'errors' in data:
        return {"error": f"Error fetching data for {username}: {data['errors']}"}, 400

    return data['data'], 200

# Route to get LeetCode data (POST request)
@app.route('/leetcode', methods=['POST'])
def leetcode_user_data():
    request_data = request.get_json()
    
    if not request_data or 'username' not in request_data:
        return jsonify({"error": "Please provide a username"}), 400
    
    username = request_data['username']
    data, status_code = get_leetcode_graphql_data(username)
    
    if status_code != 200:
        return jsonify(data), status_code
    
    return jsonify(data), 200

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
