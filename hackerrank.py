import requests
from bs4 import BeautifulSoup

def extract_hacker_rank_data(username):
    # Construct the URL for the user's profile page
    url = f"https://www.hackerrank.com/{username}"

    # Set up headers to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    # Send a GET request to fetch the HTML content of the profile
    response = requests.get(url, headers=headers)

    # Check if the request was successful and not blocked by reCAPTCHA
    if response.status_code == 200:
        html_content = response.text
        # Check if reCAPTCHA is present in the content
        if "grecaptcha" in html_content:
            print("reCAPTCHA detected. Please solve it manually.")
            return None

        # Create a Beautiful Soup object
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract the name
        name_tag = soup.find('h1', class_='hr-heading-02 profile-title ellipsis')
        name = name_tag.text.strip() if name_tag else 'Name not found'

        # Extract the badges
        badges = [badge.text.strip() for badge in soup.find_all('div', class_='badge-title')]

        # Extract medals
        medals = [medal.text.strip() for medal in soup.select('.section-card.medals .medal-title')]

        # Extract education
        education = [edu.text.strip() for edu in soup.select('.section-card.education .education-title')]

        # Extract certificates
        certificates = [cert.text.strip() for cert in soup.select('.section-card.certificates .certificate-title')]

        # Return the extracted data
        return {
            "Name": name,
            "Badges": badges,
            "Medals": medals,
            "Education": education,
            "Certificates": certificates
        }
    else:
        return {"Error": f"User not found or unable to access the profile. Status code: {response.status_code}"}

# Example usage
username = "girishds"  # Replace with the desired username
user_data = extract_hacker_rank_data(username)
print(user_data)
