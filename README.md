# Stremio Jackett Addon
Elevate your Stremio experience with seamless access to Jackett torrent links, effortlessly fetching torrents for your selected movies within the Stremio interface.

# Disclaimer
This addon was made to be running only on Linux based OS and macOS.

I am not responsible for any content downloaded through this addon.

# Prerequisites
- A Real-Debrid account
- A publicly-reachable server ([Oracle](https://www.oracle.com/fr/cloud/) provide a free lifetime server for example).
- A [Jackett](https://github.com/Jackett/Jackett) server running and reachable pubicly.
- NodeJS, npm and Python 3.

# Installation
## Python API setup
- Access to your publicly-reachable server with Python installed. 
- Install aria2
    - Ubuntu/Debian
    ```sh
    sudo apt-get install aria2
    ```
    - macOS (brew installed)
    ```sh
    brew install aria2
    ```
- Copy the main.py file on your remote server
- Install Python libraries needed
    ```sh
    pip install fastapi "uvicorn[standard]"
    ```
- In main.py, adjust filters. Add or modify in line 8 everything that has to be in a torrent name to be grabbed. In line 9, add everything that has to be excluded.
- In line 13, put your Real-Debrid API key
- In line 15, add your Jackett server URL (ie. http://jackett.com:port)
- In line 16, add your Jackett API key
- In line 17, add the ID of the Jackett film category ID for the indexer you choosed
- In line 18, add the ID of the Jackett TV series category ID for the indexer you choosed
- Once this is done, start the API server
    ```sh
    uvicorn main:app --reload --host 0.0.0.0 --port 9999
    ```
    Don't forget to change '9999' with the port that you want to use
- You are now done! Your API server is reachable at http://server_ip:port

## Stremio addon setup
- On your local server with NodeJS and Python installed, clone the repository
    ```sh
    git clone https://github.com/aymene69/stremio-jackett
    ```
- In line 26 and 37, replace `your_server_ip:port` with your own API installed just before
- Once done, install dependencies
    ```sh
    npm install
    ````
- Now just run your addon, access to the link and add it to your Stremio app!
    ```
    npm start
    ```
**WARNING** This will only work locally. If you want your addon to be reachable at any time, simply deploy it on [Beamup](https://github.com/Stremio/stremio-beamup-cli). Click [here](https://github.com/Stremio/stremio-beamup-cli) to visit their repository and see how you can deploy it.
