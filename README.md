# Stremio Jackett Addon
Elevate your Stremio experience with seamless access to Jackett torrent links, effortlessly fetching torrents for your selected movies within the Stremio interface.

# Disclaimer
I am not responsible for any content downloaded through this addon.

# Prerequisites
- A Real-Debrid account.
- A [Jackett](https://github.com/Jackett/Jackett) server running and reachable pubicly.
- NodeJS, npm.

# Installation
- On your computer, clone the repository
    ```sh
    git clone https://github.com/aymene69/stremio-jackett
    ```
- Replace certain lines with your own information:
    - Line 7, replace with elements of torrent name that has to be present to be chosen
    - Line 8, replace with elements of torrent name that needs to be missing to be chosen
    - Line 9, replace with your Real-Debrid API key
    - Line 11, replace with your Jackett URL (ie. https://jackett:port)
    - Line 12, replace with your Jackett API key
    - Line 13, replace with your favorite Jackett indexer
    - Line 14, replace with indexer's movie category
    - Line 15, replace with indexer's series category
- Once done, install dependencies
    ```sh
    npm install
    ````
- Now just run your addon, access to the link and add it to your Stremio app!
    ```
    npm start
    ```
**WARNING** This will only work locally. If you want your addon to be reachable at any time, simply deploy it on [Beamup](https://github.com/Stremio/stremio-beamup-cli). Click [here](https://github.com/Stremio/stremio-beamup-cli) to visit their repository and see how you can deploy it.
