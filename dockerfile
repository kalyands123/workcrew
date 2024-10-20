FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /usr/app/src

# Copy requirements.txt first
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python script
COPY gemini.py .

# Expose port 5000 (if needed)
EXPOSE 5000

# Run the application
CMD ["python3", "gemini.py"]
