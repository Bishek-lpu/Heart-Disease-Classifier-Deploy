# Use the official Python 3.11 slim image as the base
FROM python:3.12-slim

# Set environment variables to prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required for OpenCV and other scientific libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file first to leverage Docker cache for dependencies
COPY requirements.txt .

# Install the Python dependencies
# We use --no-cache-dir to keep the image size as small as possible
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 80

# Run app using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:app"]
