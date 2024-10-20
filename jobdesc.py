from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

# Load the model and tokenizer
model_name = "gpt2"  # You can use other variants like 'gpt2-medium', 'gpt2-large', etc.
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

# Function to generate a job description for a software developer
def generate_job_description():
    # Prompt to generate job description in a single line
    input_text = "Generate a job description for a 5 years of exprience software developer"
    
    input_ids = tokenizer.encode(input_text, return_tensors='pt')
    
    # Create attention mask
    attention_mask = torch.ones(input_ids.shape, dtype=torch.long)

    # Generate job description
    output = model.generate(input_ids, attention_mask=attention_mask, max_length=600, 
                            num_return_sequences=1, do_sample=True,  # Enable sampling
                            no_repeat_ngram_size=2, early_stopping=False,
                            temperature=0.7,  # Control randomness
                            top_p=0.9)  # Use nucleus sampling

    # Decode the generated text
    job_description = tokenizer.decode(output[0], skip_special_tokens=True)
    
    return job_description

# Example usage
job_description = generate_job_description()
print(job_description)
