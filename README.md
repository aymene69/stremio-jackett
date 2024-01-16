# Stremio Jackett Addon
Elevate your Stremio experience with seamless access to Jackett torrent links, effortlessly fetching torrents for your selected movies within the Stremio interface.

Addon accessible publicly! Configure it for you [here](https://va-dda.click/)!

# Disclaimer
I am not responsible for any content downloaded through this addon.

# Prerequisites
- A [Jackett](https://github.com/Jackett/Jackett) server running and reachable pubicly.
- NodeJS, npm.
- *(optionnal)* A Real-Debrid account.

# Installation
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
