[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/P5P2TUSN3)

# Stremio Jackett Addon
Elevate your Stremio experience with seamless access to Jackett torrent links, effortlessly fetching torrents for your selected movies within the Stremio interface.

# Disclaimer
I am not responsible for any content downloaded through this addon.

# Support on Discord [here](https://discord.gg/7yZ5PzaPYb)

# Prerequisites
- A [Jackett](https://github.com/Jackett/Jackett) server running and reachable pubicly.
- NodeJS, npm.
- *(optionnal)* A Real-Debrid, All-Debrid or Premiumize account.

# Installation
## If you are a newbie, check the [wiki](https://github.com/aymene69/stremio-jackett/wiki)

## Without Docker
- On your computer, clone the repository
    ```sh
    git clone https://github.com/aymene69/stremio-jackett
    ```
- Once done, install dependencies
    ```sh
    npm install
    ````
- Copy `.env.example` to `.env` and modify it if needed
    ```sh
    cp .env.example .env
    ````
- Build the addon
    ```sh
    npm run build
    ````
- Now just run your addon, access the link and add it to your Stremio app!
    ```
    npm start
    ```
    And access it via `your_ip:3000`
## With Docker
- Simply run the Docker image
    ```sh
    docker run -p 3000:3000 -d belmeg/stremio-addon-jackett
    ```
    And access it via `your_ip:3000`
**WARNING** This will only work locally. If you want your addon to be reachable at any time, simply deploy it on [Beamup](https://github.com/Stremio/stremio-beamup-cli). Click [here](https://github.com/Stremio/stremio-beamup-cli) to visit their repository and see how you can deploy it.

  - To update your container

    - Find your existing container name
    ```sh
    docker ps
    ```

    - Stop your existing container
    ```sh
    docker stop <CONTAINER_ID>
    ```

    - Remove your existing container
    ```sh
    docker rm <CONTAINER_ID>
    ```

    - Pull the latest version from docker hub
    ```sh
    docker pull belmeg/stremio-addon-jackett:latest
    ```

  - Finally, rerun your docker run command found in step one

## With Docker compose (Recommended) (includes Jackett and Flaresolverr)
  - Use the docker-compose.yml from the repo

  - To start the stack
   ```sh
      docker compose up -d
   ```
  - To stop the stack
   ```sh
      docker compose down
   ```
  - To pull the latest image.
   ```sh
      docker pull belmeg/stremio-addon-jackett:latest
   ```
And access it via `your_ip:3000`

I recommend also deploying Nginx Proxy Manager and securing your network with SSL.

## Scraper
Scraper is available under /scraper
