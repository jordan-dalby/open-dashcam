# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the Python script to the working directory
COPY /src .

# Install any necessary dependencies
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install opencv-python flask

EXPOSE 5000

# Set the command to run the Python script
CMD ["python", "main.py"]