# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies (if needed later you can add more)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirement file and install Python dependencies
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app

# Expose port 5000 for Flask
EXPOSE 5000

# Set environment variables for Flask (optional but clean)
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Run the Flask app
CMD ["python", "app.py"]
