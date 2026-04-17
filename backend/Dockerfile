# Use official Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
# We expect chatbot.py to be in the same directory as Dockerfile or one level up
# In docker-compose, we will mount the root to /app or copy it
COPY chatbot.py .

# Expose port 8000
EXPOSE 8000

# Run uvicorn
CMD ["uvicorn", "chatbot:app", "--host", "0.0.0.0", "--port", "8000"]
