import requests
import json
import time


def get_stream_link_pm(query, config):
    magnet = json.loads(query)['magnet']
    stream_type = json.loads(query)['type']
    url = f"https://www.premiumize.me/api/transfer/create?apikey={config['debridKey']}"
    form = {
        'src': magnet
    }
    response = requests.post(url, data=form)
    data = response.json()
    tries = 0
    id = data['id']
    item_id = 0
    is_folder = False
    while True:
        if tries > 0:
            break
        url = "https://www.premiumize.me/api/transfer/list?apikey=" + config['debridKey']
        response = requests.get(url)
        data = response.json()
        for item in data['transfers']:
            if item['id'] == id:
                if item['status'] == "finished":
                    if item['folder_id'] is None:
                        item_id = item['file_id']
                        break
                    else:
                        item_id = item['folder_id']
                        is_folder = True
                        break
        tries += 1
        time.sleep(5)
    if item_id == 0:
        return "https://github.com/aymene69/stremio-jackett/raw/main/nocache.mp4"
    if stream_type == "movie":
        if is_folder:
            url = "https://www.premiumize.me/api/folder/list?id=" + item_id + "&apikey=" + config['debridKey']
            response = requests.get(url)
            data = response.json()
            link = max(data["content"], key=lambda x: x["size"])["link"]
            return link
        else:
            url = "https://www.premiumize.me/api/item/details?id=" + item_id + "&apikey=" + config['debridKey']
            response = requests.get(url)
            data = response.json()
            link = data['link']
            return link
        url = "https://www.premiumize.me/api/folder/list?id=" + item_id + "&apikey=" + config['debridKey']
        response = requests.get(url)
        data = response.json()
        link = max(data["content"], key=lambda x: x["size"])["link"]
        return link
    if stream_type == "series":
        season_episode = json.loads(query)['season'] + json.loads(query)['episode']
        if is_folder:
            url = "https://www.premiumize.me/api/folder/list?id=" + item_id + "&apikey=" + config['debridKey']
            response = requests.get(url)
            data = response.json()
            link = next((link["link"] for link in data["content"] if season_episode in link["name"]), None)
            return link
        else:
            url = "https://www.premiumize.me/api/item/details?id=" + item_id + "&apikey=" + config['debridKey']
            response = requests.get(url)
            data = response.json()
            link = data['link']
            return link
