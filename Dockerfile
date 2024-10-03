# Use a base image with Python
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy requirements.txt first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Install Node.js and npm for Sass compilation
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && npm install -g sass \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN sass static/sass/styles.scss static/css/styles.css

# Set the command to run your app
CMD ["gunicorn", "-b", ":8080", "main:app"]
