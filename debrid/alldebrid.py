import requests
import json
from utils.get_config import get_config


def get_stream_link_ad(query, config):
    magnet = json.loads(query)['magnet']
    stream_type = json.loads(query)['type']
    config = get_config()
    url = "https://api.alldebrid.com/v4/magnet/upload?agent=jackett&apikey=" + config['debridKey'] + "&magnet=" + magnet
    response = requests.get(url)
    data = response.json()
    while True:
        url = ("https://api.alldebrid.com/v4/magnet/status?agent=jackett&apikey=" + config['debridKey'] + "&id=" +
               str(data["data"]['magnets'][0]['id']))
        response = requests.get(url)
        data = response.json()
        if data["data"]["magnets"]["status"] == "Ready":
            break
    if stream_type == "movie":
        link = max(data["data"]["magnets"]['links'], key=lambda x: x['size'])['link']
        url = "https://api.alldebrid.com/v4/link/unlock?agent=jackett&apikey=" + config['debridKey'] + "&link=" + link
        response = requests.get(url)
        data = response.json()
        link = data["data"]["link"]
        return link
    if stream_type == "series":
        season_episode = json.loads(query)['season'] + json.loads(query)['episode']
        link = next((link["link"] for link in data["data"]["magnets"]["links"] if
                    season_episode in link["filename"]), None)
        url = "https://api.alldebrid.com/v4/link/unlock?agent=jackett&apikey=" + config['debridKey'] + "&link=" + link
        response = requests.get(url)
        data = response.json()
        link = data["data"]["link"]
        return link
