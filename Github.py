import requests
import json

# Replace this with your GitHub Personal Access Token
GITHUB_TOKEN = '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 '

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
        print(f"Error fetching user data for {username}: {user_response.status_code}")
        return None

    user_data = user_response.json()
    
    # Display some general profile data
    profile_info = {
        "Name": user_data.get("name"),
        "Username": user_data.get("login"),
        "Location": user_data.get("location"),
        "Public Repos": user_data.get("public_repos"),
        "Followers": user_data.get("followers"),
        "Following": user_data.get("following"),
        "Profile URL": user_data.get("html_url")
    }

    print("Profile Info for", username)
    print(json.dumps(profile_info, indent=4))

    # Fetch repositories
    repos_url = f"https://api.github.com/users/{username}/repos"
    repos_response = requests.get(repos_url, headers=headers)
    
    if repos_response.status_code != 200:
        print(f"Error fetching repos data for {username}: {repos_response.status_code}")
        return None

    repos_data = repos_response.json()

    print("\nRepositories Info for", username)
    for repo in repos_data:
        repo_info = {
            "Repo Name": repo["name"],
            "Description": repo["description"],
            "Language": repo["language"],
            "Stars": repo["stargazers_count"],
            "Forks": repo["forks_count"],
            "Repo URL": repo["html_url"]
        }
        print(json.dumps(repo_info, indent=4))


# Example usage:
usernames = ["vigneshherao", "kalyands8050"]  # Replace with the GitHub usernames you want to extract data from
for username in usernames:
    get_github_user_data(username)
