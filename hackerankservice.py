from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Function to scrape HackerRank profile data
def get_hackerrank_stats(username):
    try:
        # HackerRank profile URL
        url = f'https://www.hackerrank.com/{username}'
        
        # Send a GET request to the HackerRank profile page
        response = requests.get(url)
        
        if response.status_code != 200:
            return {'error': f'Unable to access HackerRank profile for {username}. Status code: {response.status_code}'}, response.status_code

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Data structure to store extracted data
        data = {
            'username': username,
            'profile_name': None,
            'badges': {},
            'certificates': [],
            'education': []
        }

        # Extract profile name
        try:
            profile_name_tag = soup.find('h1', class_='profile-heading')
            if profile_name_tag:
                data['profile_name'] = profile_name_tag.text.strip()
        except Exception as e:
            print(f"Profile name not found for user {username}: {e}")

        # Extract badges
        try:
            badges_section = soup.find('section', class_='section-card hacker-badges')
            if badges_section:
                badges = badges_section.find_all('div', class_='hacker-badge')
                for badge in badges:
                    badge_name = badge.find('text').text.strip()
                    stars = len(badge.find_all('svg', class_='badge-star'))
                    data['badges'][badge_name] = f"{stars} star(s)"
        except Exception as e:
            print(f"No badges found for user {username}: {e}")

        # Extract certificates (if available)
        try:
            certificates_section = soup.find('div', class_='hacker-certificates')
            if certificates_section:
                certificates = certificates_section.find_all('a')
                for certificate in certificates:
                    certificate_name = certificate.find('h2', class_='certificate-heading').text.strip()
                    data['certificates'].append(certificate_name)
        except Exception as e:
            print(f"No certificates found for user {username}: {e}")

        # Extract education (if available)
        try:
            education_section = soup.find('ul', class_='ui-timeline')
            if education_section:
                education_items = education_section.find_all('li')
                for item in education_items:
                    institute = item.find('h2').text.strip()
                    stream = item.find('p').text.strip()
                    data['education'].append({'institute': institute, 'stream': stream})
        except Exception as e:
            print(f"No education info found for user {username}: {e}")

        return data, 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return {}, 500

# Flask route to get HackerRank stats via POST API
@app.route('/hackerrank', methods=['POST'])
def get_stats():
    # Ensure the request is in JSON format
    if request.is_json:
        req_data = request.get_json()
        username = req_data.get('username', None)
        
        if not username:
            return jsonify({'error': 'Username parameter is missing'}), 400

        # Call the function to get the stats
        stats, status_code = get_hackerrank_stats(username)
        return jsonify(stats), status_code
    else:
        return jsonify({'error': 'Request content-type must be application/json'}), 400

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
