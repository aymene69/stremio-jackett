#!/bin/bash

echo "Please enter your email: "
read userMail

echo "Please enter your domain name: "
read domainName
cd jackett
sudo rm -rf data
sudo docker compose down
cd ../addon
sudo rm -rf data
sudo docker compose down
cd ../traefik
sudo docker compose down
cd ..

sudo mkdir /etc/traefik
sudo mkdir /etc/traefik/certs

sudo curl -fsSL https://raw.githubusercontent.com/aymene69/stremio-jackett/main/traefik/traefik.yml -o /etc/traefik/traefik.yml

sudo sed -i "s/youremail@domain.com/$userMail/g" /etc/traefik/traefik.yml

sudo mkdir traefik jackett addon
sudo curl -fsSL https://raw.githubusercontent.com/aymene69/stremio-jackett/main/traefik/docker-compose.yml -o ./traefik/docker-compose.yml

sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo netfilter-persistent save
cd traefik
sudo docker compose up -d
cd ../jackett
sudo mkdir data blackhole
sudo curl -fsSL https://raw.githubusercontent.com/aymene69/stremio-jackett/main/jackett/docker-compose.yml -o ./docker-compose.yml
sudo sed -i "s/YOURADDON.COM/$domainName/g" ./docker-compose.yml
sudo docker compose up -d

cd ../addon
sudo curl -fsSL https://raw.githubusercontent.com/aymene69/stremio-jackett/main/docker-compose-traefik.yml -o ./docker-compose.yml
sudo sed -i "s/YOURADDON.COM/$domainName/g" ./docker-compose.yml
sudo docker compose up -d
cd ../traefik
sudo docker compose down
sudo docker compose up -d
clear

echo "Your addon is accessible at https://$domainName/"
echo "Jackett is accessible at http://$(curl -4 -s ifconfig.me):9117"
echo "FlareSolverr is accessible at http://$(curl -4 -s ifconfig.me):8191"