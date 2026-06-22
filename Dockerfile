# Use official Python runtime as a parent image
FROM python:3.9-slim

# Set working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories for uploads and db
RUN mkdir -p /app/instance
RUN mkdir -p /app/static/uploads/products/thumbs

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Command to run the application using Gunicorn
CMD ["sh", "-c", "python database/init_db.py && exec gunicorn --bind 0.0.0.0:5000 --workers 3 --timeout 120 'app:create_app()'"]
