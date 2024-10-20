from flask import Flask, request, jsonify
import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

app = Flask(__name__)

# Fetch GitHub user data
def get_github_user_data(username):
    user_url = f"https://api.github.com/users/{username}"
    user_response = requests.get(user_url)

    if user_response.status_code != 200:
        print(f"Error fetching GitHub user data: {user_response.status_code}")
        return {}

    user_data = user_response.json()

    repos_url = f"https://api.github.com/users/{username}/repos"
    repos_response = requests.get(repos_url)

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

# Fetch HackerRank stats using Selenium
def get_hackerrank_stats(username):
    try:
        # Set up the Chrome WebDriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        
        # Open the HackerRank profile page
        url = f'https://www.hackerrank.com/{username}'
        driver.get(url)
        
        # Wait for the page to load
        time.sleep(5)  # Adjust sleep time as necessary

        # Final output data
        data = {
            'username': username,
            'profile_name': None,
            'badges': [],
            'certificates': [],
            'education': []
        }

        # Extract profile information
        try:
            profile_name_tag = driver.find_element(By.CSS_SELECTOR, 'h1.profile-heading')
            data['profile_name'] = profile_name_tag.text.strip()
        except Exception as e:
            print(f"Profile name not found for user {username}: {e}")

        # Extract badges
        try:
            badges_div = driver.find_element(By.CSS_SELECTOR, 'section.section-card.hacker-badges')
            badges_items = badges_div.find_elements(By.CSS_SELECTOR, 'div.hacker-badge')
            for badge in badges_items:
                badge_name = badge.find_element(By.CSS_SELECTOR, 'text').text.strip()
                stars = len(badge.find_elements(By.CSS_SELECTOR, 'svg.badge-star'))
                data['badges'].append(f"{badge_name}: {stars} star(s)")
        except Exception as e:
            print(f"No badges found for user {username}: {e}")

        # Extract certificates (if available)
        try:
            certificates_div = driver.find_element(By.CSS_SELECTOR, 'div.hacker-certificates')
            certificates = certificates_div.find_elements(By.TAG_NAME, 'a')
            for certificate in certificates:
                certificate_name = certificate.find_element(By.CSS_SELECTOR, 'h2.certificate-heading').text.strip()
                data['certificates'].append(certificate_name)
        except Exception as e:
            print(f"No certificates found for user {username}: {e}")

        # Extract education (if available)
        try:
            education_div = driver.find_element(By.CSS_SELECTOR, 'ul.ui-timeline')
            education_tags = education_div.find_elements(By.TAG_NAME, 'li')
            for tag in education_tags:
                institute = tag.find_element(By.TAG_NAME, 'h2').text.strip()
                stream = tag.find_element(By.TAG_NAME, 'p').text.strip()
                data['education'].append({'institute': institute, 'stream': stream})
        except Exception as e:
            print(f"No education info found for user {username}: {e}")

        driver.quit()
        return data

    except Exception as e:
        print(f"An error occurred: {e}")
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
        candidate_skills = set(skill.lower() for skill in candidate.get('languages', []))
        matched_skills = candidate_skills.intersection(job_description_skills)

        # Update rank based on skills and LeetCode problems solved
        rank = len(matched_skills) + candidate.get('total_problems_solved', 0)
        matched_percentage = (len(matched_skills) / len(job_description_skills)) * 100 if job_description_skills else 0
        
        matched_candidates.append({
            'username': candidate['username'],
            'profile_name': candidate.get('profile_name', 'N/A'),
            'matched_skills': list(matched_skills),
            'rank': rank,
            'total_problems_solved': candidate.get('total_problems_solved', 0),
            'num_projects': candidate.get('num_projects', 0),
            'badges': candidate.get('badges', []),
            'certificates': candidate.get('certificates', []),
            'matched_percentage': matched_percentage
        })

    matched_candidates.sort(key=lambda x: x['rank'], reverse=True)

    for idx, candidate in enumerate(matched_candidates):
        candidate['rank'] = idx + 1

    return matched_candidates

# POST endpoint to receive data
@app.route('/rank_candidates', methods=['POST'])
def rank_candidates():
    data = request.json
    job_description_skills = set(data.get('job_description_skills', []))
    github_usernames = data.get('github_usernames', [])
    hackerrank_usernames = data.get('hackerrank_usernames', [])
    leetcode_usernames = data.get('leetcode_usernames', [])

    candidates_data = []

    # Fetch GitHub data
    for username in github_usernames:
        github_data = get_github_user_data(username)
        if github_data:
            candidates_data.append(github_data)

    # Fetch HackerRank data using Selenium
    for username in hackerrank_usernames:
        hackerrank_data = get_hackerrank_stats(username)
        if hackerrank_data:
            # Ensure badges and certificates are initialized
            hackerrank_data['badges'] = hackerrank_data.get('badges', [])
            hackerrank_data['certificates'] = hackerrank_data.get('certificates', [])
            
            for candidate in candidates_data:
                if candidate['username'] == hackerrank_data['username']:
                    # Update profile name if missing
                    if candidate['profile_name'] == 'N/A' and hackerrank_data['profile_name']:
                        candidate['profile_name'] = hackerrank_data['profile_name']
                    # Combine badges and certificates
                    candidate['badges'] += hackerrank_data['badges']
                    candidate['certificates'] += hackerrank_data['certificates']

    # Fetch LeetCode data
    for username in leetcode_usernames:
        leetcode_data = get_leetcode_graphql_data(username)
        if leetcode_data:
            for candidate in candidates_data:
                if candidate['username'] == leetcode_data['username']:
                    # Update profile name if missing
                    if candidate['profile_name'] == 'N/A' and leetcode_data['profile_name']:
                        candidate['profile_name'] = leetcode_data['profile_name']
                    # Update total problems solved only from LeetCode
                    candidate['total_problems_solved'] = leetcode_data.get('total_problems_solved', 0)

    # Match skills and rank candidates
    ranked_candidates = match_skills(candidates_data, job_description_skills)

    return jsonify(ranked_candidates)

if __name__ == '__main__':
    app.run(debug=True)
