# Build and run with:
# docker build -t my-python-app . && docker run -p 8502:8501 my-python-app

# Use the official Python 3.11 slim image as the base
FROM python:3.11-slim

# Set environment variables
# Prevents Python from writing pyc files to disc (optional)
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr (optional)
ENV PYTHONUNBUFFERED=1

RUN apt-get update --allow-unauthenticated

RUN apt-get install -y --no-install-recommends \
    pkg-config \
    build-essential \
    libhdf5-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and set the working directory
WORKDIR /app

# Copy everything from the current directory to /app in the container
COPY . /app/

# Install poetry
RUN pip install --upgrade pip poetry

# Install python packages with poetry
RUN poetry install

# Expose the port the app runs on
EXPOSE 8502

# Specify the command to run the app
CMD ["poetry", "run", "python3", "-m", "streamlit", "run", "app.py", "--server.port", "8502"]