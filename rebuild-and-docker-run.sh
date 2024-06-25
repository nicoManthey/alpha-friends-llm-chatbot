# run with: sudo sh rebuild-and-docker-run.sh

docker build -t alpha-friends-llm-chatbot .

# non-detached mode, app closes when logging out
docker run -p 8501:8501 alpha-friends-llm-chatbot

# detached mode, app keeps running when logging out
# docker run -d -p 8501:8501 alpha-friends-llm-chatbot

# NOTES:

# remove (all) images:
# sudo docker rm $(sudo docker ps -a -q)

# remove (all) containers:
# sudo docker rmi $(sudo docker images -q)