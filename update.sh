#!/bin/bash

cd addon
sudo docker compose down
sudo docker compose pull
sudo docker compose up -d
clear

echo "Addon updated!"
