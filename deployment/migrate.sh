#!/bin/bash

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

sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 9117 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8191 -j ACCEPT

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
sudo docker compose pull
sudo docker compose up -d
cd ../traefik
sudo docker compose up -d
clear
IP=$(curl -4 -s ifconfig.me)
echo "Your addon is accessible at https://$domainName/"
echo "Jackett is accessible at http://${IP}:9117"
echo "FlareSolverr is accessible at http://${IP}:8191"