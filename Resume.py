import os
import spacy
import json
import csv
import re
from pyresparser import ResumeParser
from pdfminer.high_level import extract_text  # To extract text from PDF files

# Load the SpaCy model
nlp = spacy.load("en_core_web_sm")

# Generalized function to extract names using spaCy NER
def extract_name_general(resume_text):
    doc = nlp(resume_text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    # Fallback to the first line assuming the name is at the top
    first_line = resume_text.split('\n')[0]
    return first_line

# Generalized function to extract company names using NLP and context-based patterns
def extract_company_names(resume_text):
    company_names = []
    company_keywords = ['Inc', 'Corp', 'Ltd', 'Technologies', 'Systems', 'Solutions', 'LLC', 'Pvt', 'Private Limited']
    
    # Use spaCy to detect organizations
    doc = nlp(resume_text)
    for ent in doc.ents:
        if ent.label_ == "ORG":
            company_names.append(ent.text)
    
    # Additional regex pattern to capture company names from context
    for line in resume_text.split('\n'):
        if any(keyword in line for keyword in company_keywords):
            company_names.append(line.strip())
    
    # Remove duplicates
    return list(set(company_names))

# Generalized function to extract college names by looking for common education-related keywords
def extract_college_names(resume_text):
    college_keywords = ['University', 'Institute', 'College', 'Academy', 'School of', 'Faculty of']
    college_names = []
    
    for line in resume_text.split('\n'):
        if any(keyword in line for keyword in college_keywords):
            college_names.append(line.strip())
    
    return list(set(college_names))

# Generalized function to extract total experience
def extract_total_experience(resume_text):
    # Pattern matching for 'X years Y months'
    experience_pattern = re.compile(r'(\d+\s+years?\s+\d+\s+months?)')
    match = experience_pattern.search(resume_text)
    if match:
        return match.group(0)
    # Alternative pattern matching for just years or months
    year_pattern = re.compile(r'(\d+\s+years?)')
    match = year_pattern.search(resume_text)
    if match:
        return match.group(0)
    return "Experience not specified"

# Specify the folder path with resume PDF files
folder_path = r"C:\Users\91901\Downloads\Tech Resume DB-20241004T133232Z-001\Tech Resume DB"  # Change this to your actual folder path

# List to hold the extracted data from all resumes
extracted_data = []

# Iterate through all the files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".pdf"):  # Process only PDF files
        resume_path = os.path.join(folder_path, filename)
        
        try:
            # Parse the resume using pyresparser
            data = ResumeParser(resume_path).get_extracted_data()

            # Extract text from the PDF for custom extraction
            resume_text = extract_text(resume_path)
            
            # Generalized name extraction
            extracted_name = extract_name_general(resume_text)
            if extracted_name:
                data['name'] = extracted_name  # Override the name field with more accurate name
            
            # Generalized company names extraction
            company_names = extract_company_names(resume_text)
            if company_names:
                data['company_names'] = company_names
            
            # Generalized total experience extraction
            total_experience = extract_total_experience(resume_text)
            if total_experience:
                data['total_experience'] = total_experience
            
            # Generalized college extraction
            extracted_colleges = extract_college_names(resume_text)
            if extracted_colleges:
                data['college_name'] = extracted_colleges

            # Append the extracted data along with filename for reference
            if data:
                data['file_name'] = filename
                extracted_data.append(data)

        except Exception as e:
            print(f"An error occurred while processing {filename}: {e}")

# Save the extracted data to a JSON file
json_output_path = r"D:\savedData.json"  # Change this to a valid output path
with open(json_output_path, 'w', encoding='utf-8') as json_file:
    json.dump(extracted_data, json_file, ensure_ascii=False, indent=4)

# Save the extracted data to a CSV file
if extracted_data:  # Only save if we have data
    csv_output_path = r"D:\savedData.csv"  # Change this to a valid output path
    csv_columns = extracted_data[0].keys()  # Get the keys from the first dict as column headers
    
    with open(csv_output_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
        writer.writeheader()
        for data in extracted_data:
            writer.writerow(data)

print(f"Data has been saved to {json_output_path} and {csv_output_path}")
