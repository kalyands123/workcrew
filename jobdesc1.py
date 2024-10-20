import requests

# Example function to generate a job description using an API (replace with Gemini API details)
def generate_job_description_gemini(input_text):
    api_endpoint =  'https://generativelanguage.googleapis.com/v1beta/{name=models/*}'
  # Replace with actual endpoint
    api_key = "AIzaSyCm8A-ip22RQQA4Cabq8_oNIXuQnZjAbGU"  # Replace with your API key
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": input_text,
        "max_tokens": 600,
        "temperature": 0.7,
        "top_p": 0.9,
        "n": 1  # Number of job descriptions to return
    }

    response = requests.post(api_endpoint, headers=headers, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        return result["text"]
    else:
        return f"Error: {response.status_code} - {response.text}"

# Example usage
user_input = input("Enter prompt for job description: ")
job_description = generate_job_description_gemini(user_input)
print(job_description)
