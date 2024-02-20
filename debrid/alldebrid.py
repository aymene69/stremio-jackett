import requests
import json
import time

def get_stream_link_ad(query, config):
    magnet = json.loads(query)['magnet']
    stream_type = json.loads(query)['type']
    url = "https://api.alldebrid.com/v4/magnet/upload?agent=jackett&apikey=" + config['debridKey'] + "&magnet=" + magnet
    response = requests.get(url)
    data = response.json()
    tries = 0
    while True:
        if tries > 5:
            break
        url = ("https://api.alldebrid.com/v4/magnet/status?agent=jackett&apikey=" + config['debridKey'] + "&id=" +
               str(data["data"]['magnets'][0]['id']))
        response = requests.get(url)
        data = response.json()
        if data["data"]["magnets"]["status"] == "Ready":
            break
        tries += 1
        time.sleep(5)
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
