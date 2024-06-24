sudo apt update

# install pip
sudo apt install python3-pip

# append path to .bashrc
echo 'export PATH="$PATH:/home/paperspace/.local/bin"' >> ~/.bashrc
source ~/.bashrc

# run install_docker.sh
sh instal_docker.sh

# Build the docker image
sudo docker build -t my-gradio .

# Run the docker image
sudo docker run -p 8001:8001 gradio-openai-demo
