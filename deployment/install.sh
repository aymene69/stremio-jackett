#!/bin/bash

sudo apt-get update -y
sudo apt-get install -y ca-certificates curl gnupg

sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update -y

sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
clear
echo "Please enter your email: "
read userMail

echo "Please enter your domain name: "
read domainName

sudo mkdir /etc/traefik
sudo mkdir /etc/traefik/certs

sudo curl -fsSL https://raw.githubusercontent.com/aymene69/stremio-jackett/main/deployment/traefik/traefik.yml -o /etc/traefik/traefik.yml

sudo sed -i "s/youremail@domain.com/$userMail/g" /etc/traefik/traefik.yml

sudo mkdir traefik jackett addon
sudo curl -fsSL https://raw.githubusercontent.com/aymene69/stremio-jackett/main/deployment/traefik/docker-compose.yml -o ./traefik/docker-compose.yml

sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo netfilter-persistent save
cd traefik
sudo docker compose up -d
cd ../jackett
sudo mkdir data blackhole
sudo curl -fsSL https://raw.githubusercontent.com/aymene69/stremio-jackett/main/deployment/jackett/docker-compose.yml -o ./docker-compose.yml
sudo sed -i "s/YOURADDON.COM/$domainName/g" ./docker-compose.yml
sudo docker compose up -d

cd ../addon
sudo curl -fsSL https://raw.githubusercontent.com/aymene69/stremio-jackett/main/deployment/docker-compose-traefik.yml -o ./docker-compose.yml
sudo sed -i "s/YOURADDON.COM/$domainName/g" ./docker-compose.yml
sudo docker compose up -d
cd ../traefik
sudo docker compose down
sudo docker compose up -d
clear

echo "Your addon is accessible at https://$domainName/"
echo "Jackett is accessible at http://$(curl -4 -s ifconfig.me):9117"
echo "FlareSolverr is accessible at http://$(curl -4 -s ifconfig.me):8191"