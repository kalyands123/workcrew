import requests
import json

def get_leetcode_graphql_data(username):
    url = 'https://leetcode.com/graphql'
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Simplified query without languages field
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
        print(f"HTTP Error {response.status_code} for user {username}")
        return None

    data = response.json()

    if 'errors' in data:
        print(f"Error fetching data for {username}: {data['errors']}")
        return None

    return data['data']

# Example usage
if __name__ == "__main__":
    leetcode_usernames = ['kalyands', 'vigneshherao','ds_girish']  # Add more usernames as needed

    for username in leetcode_usernames:
        print(f"Fetching data for {username}...")
        leetcode_data = get_leetcode_graphql_data(username)

        # Pretty-print the data
        if leetcode_data:
            print(json.dumps(leetcode_data, indent=4))

            # Extract and display the number of problems solved by difficulty
            if leetcode_data['matchedUser']['submitStats']:
                print(f"\nProblem Solving Stats for {username}:")
                for stat in leetcode_data['matchedUser']['submitStats']['acSubmissionNum']:
                    print(f"{stat['difficulty']} problems solved: {stat['count']}")
        else:
            print(f"No data found for {username}")
