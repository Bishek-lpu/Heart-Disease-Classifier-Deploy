# Use the official Python 3.11 slim image as the base
FROM python:3.11-slim

# Set environment variables to prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required for OpenCV and other scientific libraries
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file first to leverage Docker cache for dependencies
COPY requirements.txt .

# Install the Python dependencies
# We use --no-cache-dir to keep the image size as small as possible
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Render dynamically assigns a PORT environment variable, so we default to 8501 if it's missing
ENV PORT=8501

# Expose the port so external services know where to route traffic
EXPOSE $PORT

# Start the application using Gunicorn, binding it to the PORT environment variable
CMD gunicorn app:app --bind 0.0.0.0:$PORT
