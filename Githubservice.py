from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Replace this with your GitHub Personal Access Token
GITHUB_TOKEN = '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'

# Function to get GitHub user data
def get_github_user_data(username):
    # GitHub API URL for the user profile
    user_url = f"https://api.github.com/users/{username}"
    
    # Set up headers with the token for authentication
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Fetch user data
    user_response = requests.get(user_url, headers=headers)
    
    if user_response.status_code != 200:
        return {"error": f"Error fetching user data for {username}: {user_response.status_code}"}, user_response.status_code

    user_data = user_response.json()
    
    # General profile data
    profile_info = {
        "Name": user_data.get("name"),
        "Username": user_data.get("login"),
        "Location": user_data.get("location"),
        "Public Repos": user_data.get("public_repos"),
        "Followers": user_data.get("followers"),
        "Following": user_data.get("following"),
        "Profile URL": user_data.get("html_url")
    }

    # Fetch repositories
    repos_url = f"https://api.github.com/users/{username}/repos"
    repos_response = requests.get(repos_url, headers=headers)
    
    if repos_response.status_code != 200:
        return {"error": f"Error fetching repos data for {username}: {repos_response.status_code}"}, repos_response.status_code

    repos_data = repos_response.json()

    # Collect all unique languages across repositories
    all_languages = set()

    for repo in repos_data:
        # Fetch repository languages (this will give a dictionary of languages used in the repo)
        languages_url = f"https://api.github.com/repos/{username}/{repo['name']}/languages"
        languages_response = requests.get(languages_url, headers=headers)
        languages_data = languages_response.json()

        # Add the languages to the set (avoids duplicates)
        all_languages.update(languages_data.keys())

    # Sort the languages for consistent output
    sorted_languages = sorted(list(all_languages))

    # Create the final output with profile info first and all unique languages used next
    output_data = {
        "profile_info": {
            "Name": profile_info["Name"],
            "Username": profile_info["Username"],
            "Location": profile_info["Location"],
            "Followers": profile_info["Followers"],
            "Following": profile_info["Following"],
            "Public Repos": profile_info["Public Repos"],
            "Profile URL": profile_info["Profile URL"]
        },
        "languages_used": sorted_languages  # Sorted list of unique languages across all repos
    }

    return output_data, 200


# Route to fetch GitHub user data via POST request
@app.route('/github', methods=['POST'])
def github_user():
    # Get the request data (assuming it's JSON)
    request_data = request.get_json()

    # Check if 'username' field is provided in the request
    if not request_data or 'username' not in request_data:
        return jsonify({"error": "Username is required"}), 400

    # Extract the GitHub username from the request data
    username = request_data['username']

    # Fetch GitHub user data
    data, status_code = get_github_user_data(username)
    return jsonify(data), status_code


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
