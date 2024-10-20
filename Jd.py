from transformers import T5Tokenizer, T5ForConditionalGeneration

# Load the T5 model and tokenizer
model_name = "t5-small"  # You can also try 't5-base' or 't5-large'
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

# Define a more detailed prompt
prompt = "Generate a detailed job description for an e-learning software developer with 5 years of experience, including required skills, responsibilities, and qualifications."

# Prepend the task to the input
input_text = f"translate English to English: {prompt}"
input_ids = tokenizer.encode(input_text, return_tensors="pt")

# Generate the job description
output = model.generate(
    input_ids,
    max_length=250,  # Increase the length for more detailed output
    num_return_sequences=1,
    num_beams=5,  # Set beams to more than 1 for better quality
    early_stopping=True
)

# Decode the generated output
job_description = tokenizer.decode(output[0], skip_special_tokens=True)

# Print the generated job description
print(job_description)
