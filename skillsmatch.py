import requests
import json
from bs4 import BeautifulSoup

# Replace this with your GitHub Personal Access Token
GITHUB_TOKEN = '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'

# Fetch GitHub user data
def get_github_user_data(username):
    user_url = f"https://api.github.com/users/{username}"
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}'  # Add authorization header
    }
    user_response = requests.get(user_url, headers=headers)

    if user_response.status_code != 200:
        print(f"Error fetching GitHub user data: {user_response.status_code}")
        return {}

    user_data = user_response.json()

    repos_url = f"https://api.github.com/users/{username}/repos"
    repos_response = requests.get(repos_url, headers=headers)  # Include headers

    if repos_response.status_code != 200:
        print(f"Error fetching GitHub repos data: {repos_response.status_code}")
        return {}

    repos_data = repos_response.json()

    languages_used = set()
    num_projects = len(repos_data)  # Number of projects (public repos)

    for repo in repos_data:
        language = repo.get('language')
        if language:
            languages_used.add(language.lower())  # Add the language to the set

    return {
        'username': username,
        'profile_name': user_data.get('name', 'N/A'),
        'languages': languages_used,
        'num_projects': num_projects  # Number of projects from GitHub
    }

# Fetch HackerRank stats
def get_hackerrank_stats(username):
    try:
        url = f'https://www.hackerrank.com/{username}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0'
        }

        page = requests.get(url, headers=headers)
        if page.status_code != 200:
            print(f"Failed to retrieve data for {username}: {page.status_code}")
            return {}

        soup = BeautifulSoup(page.content, 'html.parser')

        data = {
            'username': username,
            'profile_name': None,
            'total_problems_solved': 0  # Initialize with 0
        }

        # Extract profile name
        profile_name = soup.find('div', {'class': 'profile-heading'})
        if profile_name:
            data['profile_name'] = profile_name.find('h1').get_text(strip=True)

        # Extract total problems solved (assuming it's available on the profile page)
        problems_solved_div = soup.find('div', {'class': 'profile-badge'})
        if problems_solved_div:
            try:
                total_problems_solved = int(problems_solved_div.find('span').get_text(strip=True))
                data['total_problems_solved'] = total_problems_solved
            except (ValueError, AttributeError):
                data['total_problems_solved'] = 0

        return data

    except requests.exceptions.RequestException as e:
        print(f"Request error for {username}: {e}")
        return {}

# Fetch LeetCode data
def get_leetcode_graphql_data(username):
    url = 'https://leetcode.com/graphql'
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    query = f'''
    {{
        matchedUser(username: "{username}") {{
            username
            profile {{
                realName
            }}
            submitStats {{
                acSubmissionNum {{
                    difficulty
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

    leetcode_data = data['data']['matchedUser']
    total_solved = sum(stat['count'] for stat in leetcode_data['submitStats']['acSubmissionNum'])

    return {
        'username': leetcode_data['username'],
        'profile_name': leetcode_data['profile']['realName'],
        'total_problems_solved': total_solved
    }

# Match skills and rank candidates
def match_skills(candidates, job_description_skills):
    matched_candidates = []

    for candidate in candidates:
        candidate_skills = set(skill.lower() for skill in candidate.get('skills', []))
        matched_skills = candidate_skills.intersection(job_description_skills)

        github_languages = candidate.get('languages', set())
        matched_skills.update(github_languages.intersection(job_description_skills))

        rank = len(matched_skills) + candidate.get('total_problems_solved', 0)
        matched_candidates.append({
            'username': candidate['username'],
            'profile_name': candidate.get('profile_name', 'N/A'),
            'matched_skills': list(matched_skills),
            'rank': rank,
            'total_problems_solved': candidate.get('total_problems_solved', 0),
            'num_projects': candidate.get('num_projects', 0)  # Add number of projects
        })

    matched_candidates.sort(key=lambda x: x['rank'], reverse=True)

    for idx, candidate in enumerate(matched_candidates):
        candidate['rank'] = idx + 1

    return matched_candidates

# Example usage
if __name__ == "__main__":
    job_description_skills = {"python", "java", "c++", "javascript", "django", "machine learning", "data analysis"}
    github_usernames = ['kalyands123', 'vigneshherao']
    hackerrank_usernames = ['kalyands8050', 'vigneshherao']
    leetcode_usernames = ['kalyands', 'vigneshherao']

    candidates_data = []

    # Fetch GitHub data
    for username in github_usernames:
        github_data = get_github_user_data(username)
        if github_data:
            candidates_data.append(github_data)

    # Fetch HackerRank data
    for username in hackerrank_usernames:
        hackerrank_data = get_hackerrank_stats(username)
        if hackerrank_data:
            for candidate in candidates_data:
                if candidate['username'] == hackerrank_data['username']:
                    candidate['profile_name'] = hackerrank_data['profile_name'] or candidate.get('profile_name', 'N/A')
                    candidate['total_problems_solved'] = hackerrank_data['total_problems_solved']

    # Fetch LeetCode data
    for username in leetcode_usernames:
        leetcode_data = get_leetcode_graphql_data(username)
        if leetcode_data:
            for candidate in candidates_data:
                if candidate['username'] == leetcode_data['username']:
                    candidate['profile_name'] = leetcode_data['profile_name'] or candidate.get('profile_name', 'N/A')
                    candidate['total_problems_solved'] += leetcode_data['total_problems_solved']

    # Match skills and rank candidates
    ranked_candidates = match_skills(candidates_data, job_description_skills)

    for candidate in ranked_candidates:
        print(f"Username: {candidate['username']}, Profile Name: {candidate['profile_name']}, "
              f"Matched Skills: {candidate['matched_skills']}, Rank: {candidate['rank']}, "
              f"Total Problems Solved: {candidate['total_problems_solved']}, Projects on GitHub: {candidate['num_projects']}")
