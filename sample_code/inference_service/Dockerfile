# Use a base image with Python and NVIDIA CUDA support for GPU acceleration
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive

# Install Python and other system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Set python3 as the default python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Set up the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
# This is done in a separate step to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY main.py .

# Expose the port the app runs on
EXPOSE 8000

# Define the command to run the application
# This will start the Uvicorn server, making the API accessible.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
