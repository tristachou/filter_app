# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install ffmpeg and its dependencies
# Using --no-install-recommends to keep the image size smaller
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code into the container at /app
COPY . .

# Expose the port that the app runs on
EXPOSE 8000

# Define environment variable for FastAPI
ENV PYTHONPATH=/app

# Run the application
# Use uvicorn to run the FastAPI app, binding to 0.0.0.0 for external access
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]