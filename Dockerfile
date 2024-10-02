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

# Install gunicorn
RUN pip install gunicorn

# Set the command to run your app
CMD ["gunicorn", "-b", ":8080", "main:app"]
