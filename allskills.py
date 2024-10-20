import requests
import json
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager

# Fetch GitHub user data
def get_github_user_data(username):
    user_url = f"https://api.github.com/users/{username}"
    user_response = requests.get(user_url)

    if user_response.status_code != 200:
        print(f"Error fetching GitHub user data for {username}: {user_response.status_code}")
        return {}

    user_data = user_response.json()
    repos_url = f"https://api.github.com/users/{username}/repos"
    repos_response = requests.get(repos_url)

    if repos_response.status_code != 200:
        print(f"Error fetching GitHub repos data for {username}: {repos_response.status_code}")
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
        # Set up Firefox WebDriver
        firefox_options = Options()
        firefox_options.add_argument("--headless")  # Headless mode
        firefox_options.add_argument("--disable-gpu")  # Disable GPU acceleration (optional)
        firefox_options.add_argument("--no-sandbox")  # Bypass OS security model

        driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=firefox_options)
        
        # Open the HackerRank profile page
        url = f'https://www.hackerrank.com/{username}'
        driver.get(url)

        # WebDriverWait to ensure elements are loaded before accessing them
        wait = WebDriverWait(driver, 10)  # Wait for up to 10 seconds for elements to appear

        # Final output data
        data = {
            'username': username,
            'profile_name': None,
            'badges': [],
            'certificates': [],
            'num_projects': 0  # Placeholder for projects
        }

        # Extract profile name
        try:
            profile_name_tag = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.profile-heading')))
            data['profile_name'] = profile_name_tag.text.strip()
        except Exception as e:
            print(f"Profile name not found for user {username}: {e}")

        # Extract badges
        try:
            badges_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'section.section-card.hacker-badges')))
            badges_items = badges_div.find_elements(By.CSS_SELECTOR, 'div.hacker-badge')
            for badge in badges_items:
                badge_name = badge.find_element(By.CSS_SELECTOR, 'text').text.strip()
                stars = len(badge.find_elements(By.CSS_SELECTOR, 'svg.badge-star'))
                data['badges'].append(f"{badge_name}: {stars} star(s)")
        except Exception as e:
            print(f"No badges found for user {username}: {e}")

        # Extract certificates (if available)
        try:
            certificates_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.hacker-certificates')))
            certificates = certificates_div.find_elements(By.TAG_NAME, 'a')
            for certificate in certificates:
                certificate_name = certificate.find_element(By.CSS_SELECTOR, 'h2.certificate-heading').text.strip()
                data['certificates'].append(certificate_name)
        except Exception as e:
            print(f"No certificates found for user {username}: {e}")

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

# Fetch candidate data based on input format
def fetch_candidate_data(candidate_ids):
    candidates_data = []

    for platform, username in candidate_ids.items():
        if platform == 'github':
            github_data = get_github_user_data(username)
            if github_data:
                candidates_data.append({'github': github_data})

        elif platform == 'hackerrank':
            hackerrank_data = get_hackerrank_stats(username)
            if hackerrank_data:
                candidates_data.append({'hackerrank': hackerrank_data})

        elif platform == 'leetcode':
            leetcode_data = get_leetcode_graphql_data(username)
            if leetcode_data:
                candidates_data.append({'leetcode': leetcode_data})

    return candidates_data

# Example usage
if __name__ == "__main__":
    job_description_skills = {"python", "java", "javascript", "machine learning", "data analysis"}
    candidate_ids = {
        'github': 'vigneshherao',
        'hackerrank': 'vigneshherao',
        'leetcode': 'vigneshherao'  # Assuming 'kalyands' is the correct username for LeetCode
    }

    # Add more candidates
    additional_candidate_ids = {
        'github': 'kalyands123',
        'hackerrank': 'kalyands8050',
        'leetcode': 'kalyands'
    }
    additional_candidate_ids = {
        'github': '',
        'hackerrank': 'girishds97',
        'leetcode': 'ds_girish'
    }

    # Fetch candidate data
    candidates_data = fetch_candidate_data(candidate_ids)
    additional_candidates_data = fetch_candidate_data(additional_candidate_ids)

    # Combine candidate data
    combined_candidates = {}
    
    for candidate in candidates_data + additional_candidates_data:
        for platform, data in candidate.items():
            username = data['username']
            if username not in combined_candidates:
                combined_candidates[username] = {'leetcode': {}, 'hackerrank': {}, 'github': {}}
            combined_candidates[username][platform] = data

    # Prepare the output format
    output = []
    for username, platforms in combined_candidates.items():
        output.append({
            'username': username,
            'leetcode': platforms['leetcode'],
            'hackerrank': platforms['hackerrank'],
            'github': platforms['github']
        })

    # Match skills and rank candidates
    ranked_candidates = match_skills(output, job_description_skills)

    # Print results
    for candidate in ranked_candidates:
        print(f"Username: {candidate['username']}")
        print(f"Profile Name: {candidate['profile_name']}")
        print(f"Matched Skills: {candidate['matched_skills']}")
        print(f"Total Problems Solved (LeetCode): {candidate['total_problems_solved']}")
        print(f"Rank: {candidate['rank']}")
        print(f"Num Projects (GitHub): {candidate['num_projects']}")
        print(f"Badges (HackerRank): {', '.join(candidate['badges']) if candidate['badges'] else 'None'}")
        print(f"Certificates (HackerRank): {', '.join(candidate['certificates']) if candidate['certificates'] else 'None'}")
        print(f"Matched Percentage: {candidate['matched_percentage']:.2f}%")
        print()
