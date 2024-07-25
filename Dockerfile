# Use the official Python image from the Docker Hub
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install necessary dependencies
RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6 wget gnupg software-properties-common cmake

# Install CMake from Kitware APT repository to get the latest version
#RUN wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc | apt-key add - && \
#    apt-add-repository 'deb https://apt.kitware.com/ubuntu/ focal main' && \
#    apt-get update && \
#    apt-get install -y cmake

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install opencv-python-headless flask

# Expose the port the app runs on
EXPOSE 5000

# Define the command to run the app
CMD ["python", "app.py"]
