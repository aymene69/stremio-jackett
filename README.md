[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/P5P2TUSN3)

# Stremio Jackett Addon
Elevate your Stremio experience with seamless access to Jackett torrent links, effortlessly fetching torrents for your selected movies within the Stremio interface.

# Disclaimer
I am not responsible for any content downloaded through this addon.

# Support on Discord [here](https://discord.gg/7yZ5PzaPYb)

# Prerequisites
- A [Jackett](https://github.com/Jackett/Jackett) server running and reachable pubicly.
- NodeJS, npm.
- *(optionnal)* A Real-Debrid or All-Debrid account.

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
- Now just run your addon, access to the link and add it to your Stremio app!
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

## With Docker compose (Recommended)

    - Create a docker-compose.yml file with the following contents

```sh
name: stremio_jacket
services:
  flaresolverr:
    image: ghcr.io/flaresolverr/flaresolverr:latest
    container_name: flaresolverr
    environment:
      - LOG_LEVEL=${LOG_LEVEL:-info}
      - LOG_HTML=${LOG_HTML:-false}
      - CAPTCHA_SOLVER=${CAPTCHA_SOLVER:-none}
      - PUID=$(id -u)
      - PGID=$(id -g)
      - TZ=America/Los_Angeles
#    networks:
#      - stremio_jacket_network
    ports:
      - "${PORT:-8191}:8191"
    restart: unless-stopped
  jackett:
    image: lscr.io/linuxserver/jackett:latest
    container_name: jackett
    environment:
      - PUID=$(id -u)
      - PGID=$(id -g)
      - TZ=America/Los_Angeles
      - AUTO_UPDATE=true #optional
      - RUN_OPTS= #optional
    depends_on:
      - flaresolverr
#    networks:
#      - stremio_jacket_network
    volumes:
      - ./data:/config
      - /path/to/blackhole:/downloads #replace /path/to/blackhole with your download directory
    ports:
      - 9117:9117
    restart: unless-stopped
  jackett-stremio:
    image: belmeg/stremio-addon-jackett
    container_name: jackett-stremio
    environment:
      - PUID=$(id -u)
      - PGID=$(id -g)
      - TZ=America/Los_Angeles
      - ADDON_NAME=stremio_jacket
    depends_on:
      - jackett
#    networks:
#      - stremio_jacket_network
    ports:
      - 3000:3000
    restart: unless-stopped
    
#networks:
#    stremio_jacket_network:
#        external: true
#        name: stremio_jacket_network
```

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
