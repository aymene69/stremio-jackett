#!/bin/bash

cd addon
sudo docker compose down
sudo docker compose pull
sudo docker compose up -d
clear
IP=$(curl -4 -s ifconfig.me)
echo "Update completed!"
echo "Your addon is accessible at https://$domainName/"