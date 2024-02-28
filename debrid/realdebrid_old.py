import requests
import json
import time

from utils.logger import setup_logger

logger = setup_logger(__name__)


def is_already_added(magnet, config):
    hash = magnet.split("urn:btih:")[1].split("&")[0].lower()
    logger.info("Getting Real-Debrid torrents")
    url = "https://api.real-debrid.com/rest/1.0/torrents"
    headers = {
        "Authorization": f"Bearer {config['debridKey']}"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    for torrent in data:
        if torrent['hash'] == hash:
            return torrent['id']
    return None


def get_stream_link_rd(query, source_ip, config):
    logger.info("Started getting Real-Debrid link")
    magnet = json.loads(query)['magnet']
    type = json.loads(query)['type']
    logger.info("Adding magnet to Real-Debrid")
    torrent_id = is_already_added(magnet, config)
    headers = {
        "Authorization": f"Bearer {config['debridKey']}"
    }
    if torrent_id:
        logger.info("Torrent already added to Real-Debrid. ID: " + torrent_id)
    else:
        url = "https://api.real-debrid.com/rest/1.0/torrents/addMagnet"
        data = {
            "magnet": magnet,
            "ip": source_ip
        }
        response = requests.post(url, headers=headers, data=data)
        data = response.json()
        torrent_id = data['id']
        logger.info("Added magnet to Real-Debrid. ID: " + torrent_id)
    logger.info("Getting torrent info")
    url = "https://api.real-debrid.com/rest/1.0/torrents/info/" + torrent_id
    response = requests.get(url, headers=headers)
    data = response.json()
    logger.info("Got torrent info")
    if type == "movie":
        logger.info("Selecting movie file")
        file = max(data['files'], key=lambda x: x['bytes'])
        logger.info("File name: " + file['path'])
        url = "https://api.real-debrid.com/rest/1.0/torrents/selectFiles/" + torrent_id
        data_payload = {
            "files": file['id'],
            "ip": source_ip
        }
        requests.post(url, headers=headers, data=data_payload)
        logger.info("Selected file")
        tries = 0
        while True:
            if tries > 0:
                return "https://github.com/aymene69/stremio-jackett/raw/main/nocache.mp4"
            logger.info("Getting link")
            url = "https://api.real-debrid.com/rest/1.0/torrents/info/" + torrent_id
            response = requests.get(url, headers=headers)
            data = response.json()
            if data['links']:
                link = data['links'][0]
                break
            tries += 1
            time.sleep(5)
        logger.info("Got link")
        logger.info("Unrestricting link")
        url = "https://api.real-debrid.com/rest/1.0/unrestrict/link"
        data = {
            "link": link,
            "ip": source_ip
        }
        response = requests.post(url, headers=headers, data=data)
        data = response.json()
        logger.info("Unrestricted link")
        return data['download']
    if type == "series":
        logger.info("Selecting series file")
        filtered_files = [file for file in data['files'] if
                          json.loads(query)['season'].lower() + json.loads(query)['episode'].lower() in file['path'].lower()]
        if not filtered_files:
            logger.error("No files found for season " + json.loads(query)['season'] + " episode " + json.loads(query)['episode'])
            return None
        file = max(filtered_files, key=lambda x: x['bytes'])
        logger.info("File name: " + file['path'])
        url = "https://api.real-debrid.com/rest/1.0/torrents/selectFiles/" + torrent_id
        data_payload = {
            "files": file['id'],
            "ip": source_ip
        }
        requests.post(url, headers=headers, data=data_payload)
        logger.info("Selected file")
        tries = 0
        while True:
            if tries > 0:
                return "https://github.com/aymene69/stremio-jackett/raw/main/nocache.mp4"
            logger.info("Getting link")
            url = "https://api.real-debrid.com/rest/1.0/torrents/info/" + torrent_id
            response = requests.get(url, headers=headers)
            data = response.json()
            if data['links']:
                link = data['links'][0]
                break
            tries += 1
            time.sleep(5)
        logger.info("Got link")
        logger.info("Unrestricting link")
        url = "https://api.real-debrid.com/rest/1.0/unrestrict/link"
        data = {
            "link": link,
            "ip": source_ip
        }
        response = requests.post(url, headers=headers, data=data)
        data = response.json()
        logger.info("Unrestricted link")
        return data['download']
