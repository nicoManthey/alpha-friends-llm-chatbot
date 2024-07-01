#!/bin/bash

# Stop and remove running containers with the name alpha-friends-llm-chatbot
docker ps -a --filter ancestor=alpha-friends-llm-chatbot --format "{{.ID}}" | xargs -I {} sh -c 'sudo docker stop {}; sudo docker rm {}'

# Remove all images with the tag alpha-friends-llm-chatbot
docker images alpha-friends-llm-chatbot --format "{{.ID}}" | xargs -I {} sudo docker rmi {}

# Build the image
sudo docker build -t alpha-friends-llm-chatbot .

# Run the container in non-detached mode
sudo docker run -p 8501:8501 alpha-friends-llm-chatbot

# To run in detached mode, uncomment the following line and comment out the above run command
# sudo docker run -d -p 8501:8501 alpha-friends-llm-chatbot