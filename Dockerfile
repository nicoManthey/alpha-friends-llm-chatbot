# Use the official Python 3.11 slim image as the base
FROM python:3.11-slim

# Set environment variables
# Prevents Python from writing pyc files to disc (optional)
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr (optional)
ENV PYTHONUNBUFFERED 1

# Install necessary system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create and set the working directory
WORKDIR /app

# Copy everything from the current directory to /app in the container
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 8501

# Specify the command to run the app
CMD ["python3", "-m", "streamlit", "run", "app.py", "--server.port", "8501"]