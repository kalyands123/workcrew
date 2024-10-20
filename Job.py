import requests
import json

# API endpoint
api_url = "https://www.arbeitnow.com/api/job-board-api"

# Make a GET request to fetch the job data
response = requests.get(api_url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the response JSON
    job_data = response.json()

    # Extract the jobs
    jobs = job_data.get("data", [])

    # Prepare a list to store job details
    job_list = []

    # Loop through each job and collect the details
    for job in jobs:
        title = job.get("title")
        company_name = job.get("company_name")
        location = job.get("location")
        description = job.get("description")
        remote = job.get("remote", False)
        visa_sponsorship = job.get("visa_sponsorship", False)

        # Check if the essential data exists
        if title and company_name:
            # Append the job details to the list
            job_list.append({
                "Job Title": title,
                "Company": company_name,
                "Location": location,
                "Remote": "Yes" if remote else "No",
                "Visa Sponsorship": "Yes" if visa_sponsorship else "No",
                "Description": description
            })

    # Save the job data to a JSON file if any job data is collected
    if job_list:
        with open("job_data.json", "w", encoding='utf-8') as json_file:
            json.dump(job_list, json_file, ensure_ascii=False, indent=4)

else:
    # Optional: Add logging or error handling here if needed
    print(f"Error: Unable to fetch job data (Status code: {response.status_code})")
