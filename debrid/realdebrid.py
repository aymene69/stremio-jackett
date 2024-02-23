import requests
import json
import time


def get_stream_link_rd(query, config):
    print("Started getting Real-Debrid link")
    magnet = json.loads(query)['magnet']
    type = json.loads(query)['type']
    print("Getting config")
    print("Got config")
    print("Adding magnet to Real-Debrid")
    torrent_id = is_already_added(magnet, config)
    headers = {
        "Authorization": f"Bearer {config['debridKey']}"
    }
    if torrent_id:
        print("Torrent already added to Real-Debrid. ID: " + torrent_id)
    else:
        url = "https://api.real-debrid.com/rest/1.0/torrents/addMagnet"
        data = {
            "magnet": magnet
        }
        response = requests.post(url, headers=headers, data=data)
        data = response.json()
        torrent_id = data['id']
        print("Added magnet to Real-Debrid. ID: " + torrent_id)
    print("Getting torrent info")
    url = "https://api.real-debrid.com/rest/1.0/torrents/info/" + torrent_id
    response = requests.get(url, headers=headers)
    data = response.json()
    print("Got torrent info")
    if type == "movie":
        print("Selecting movie file")
        file = max(data['files'], key=lambda x: x['bytes'])
        print("File name: " + file['path'])
        url = "https://api.real-debrid.com/rest/1.0/torrents/selectFiles/" + torrent_id
        data_payload = {
            "files": file['id']
        }
        requests.post(url, headers=headers, data=data_payload)
        print("Selected file")
        tries = 0
        while True:
            if tries > 0:
                return "https://github.com/aymene69/stremio-jackett/raw/main/nocache.mp4"
            print("Getting link")
            url = "https://api.real-debrid.com/rest/1.0/torrents/info/" + torrent_id
            response = requests.get(url, headers=headers)
            data = response.json()
            if data['links']:
                link = data['links'][0]
                break
            tries += 1
            time.sleep(5)
        print("Got link")
        print("Unrestricting link")
        url = "https://api.real-debrid.com/rest/1.0/unrestrict/link"
        data = {
            "link": link
        }
        response = requests.post(url, headers=headers, data=data)
        data = response.json()
        print("Unrestricted link")
        return data['download']
    if type == "series":
        print("Selecting series file")
        filtered_files = [file for file in data['files'] if json.loads(query)['season'] + json.loads(query)['episode'] in file['path']]
        file = max(filtered_files, key=lambda x: x['bytes'])
        print("File name: " + file['path'])
        url = "https://api.real-debrid.com/rest/1.0/torrents/selectFiles/" + torrent_id
        data_payload = {
            "files": file['id']
        }
        requests.post(url, headers=headers, data=data_payload)
        print("Selected file")
        tries = 0
        while True:
            if tries > 0:
                return "https://github.com/aymene69/stremio-jackett/raw/main/nocache.mp4"
            print("Getting link")
            url = "https://api.real-debrid.com/rest/1.0/torrents/info/" + torrent_id
            response = requests.get(url, headers=headers)
            data = response.json()
            if data['links']:
                link = data['links'][0]
                break
            tries +=1
            time.sleep(5)
        print("Got link")
        print("Unrestricting link")
        url = "https://api.real-debrid.com/rest/1.0/unrestrict/link"
        data = {
            "link": link
        }
        response = requests.post(url, headers=headers, data=data)
        data = response.json()
        print("Unrestricted link")
        return data['download']


def is_already_added(magnet, config):
    hash = magnet.split("urn:btih:")[1].split("&")[0].lower()
    print("Getting Real-Debrid torrents")
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
