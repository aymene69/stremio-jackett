import requests
import bencode
import hashlib
import concurrent.futures


format = [".mkv", ".mp4", ".avi", ".mov", ".flv", ".wmv", ".webm", ".mpg", ".mpeg", ".m4v", ".3gp", ".3g2", ".ogv", ".ogg", ".drc", ".gif", ".gifv", ".mng", ".avi", ".mov", ".qt", ".wmv", ".yuv", ".rm", ".rmvb", ".asf", ".amv", ".mp4", ".m4p", ".m4v", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".mpg", ".mpeg", ".m2v", ".m4v", ".svi", ".3gp", ".3g2", ".mxf", ".roq", ".nsv", ".flv", ".f4v", ".f4p", ".f4a", ".f4b"]


def get_availability_cached(stream, type, seasonEpisode=None, config=None):
    if config["service"] == "realdebrid":
        hash = stream['magnet'].split("urn:btih:")[1].split("&")[0]
        url = "https://api.real-debrid.com/rest/1.0/torrents/instantAvailability/" + hash
        headers = {
            "Authorization": f"Bearer {config['debridKey']}"
        }
        response = requests.get(url, headers=headers)
        data = response.json()
        results = next(iter(data.items()))[1]
        if len(results) > 0:
            if type == "movie":
                return True
            if type == "series":
                for result in results['rd']:
                    for file in result.items():
                        if seasonEpisode in file[1]['filename']:
                            return True
                return False
            return True
        else:
            return False
    if config["service"] == "alldebrid":
        url = "https://api.alldebrid.com/v4/magnet/instant?agent=jackett&apikey=" + config[
            'debridKey'] + "&magnets[]=" + stream['magnet']
        response = requests.get(url)
        data = response.json()
        if data["data"]["magnets"][0]["instant"]:
            if type == "movie":
                return True
            if type == "series":
                for file in data["data"]["magnets"][0]["files"]:
                    if seasonEpisode in file["n"]:
                        return True
                return False
            return True


def is_available(magnet, type, seasonEpisode=None, config=None):
    if config["service"] == "realdebrid":
        hash = magnet.split("urn:btih:")[1].split("&")[0]
        url = "https://api.real-debrid.com/rest/1.0/torrents/instantAvailability/" + hash
        headers = {
            "Authorization": f"Bearer {config['debridKey']}"
        }
        response = requests.get(url, headers=headers)
        data = response.json()
        results = next(iter(data.items()))[1]
        if len(results) > 0:
            if type == "movie":
                return True
            if type == "series":
                for result in results['rd']:
                    for file in result.items():
                        if seasonEpisode in file[1]['filename']:
                            return True
                return False
            return True
        else:
            return False
    if config["service"] == "alldebrid":
        url = "https://api.alldebrid.com/v4/magnet/instant?agent=jackett&apikey=" + config['debridKey'] + "&magnets[]=" + magnet
        response = requests.get(url)
        data = response.json()
        if data["data"]["magnets"][0]["instant"]:
            if type == "movie":
                return True
            if type == "series":
                for file in data["data"]["magnets"][0]["files"]:
                    if seasonEpisode in file["n"]:
                        return True
                return False
            return True


def get_torrent_info(item, config):
    if item['link'].startswith("magnet:"):
        magnet_link = item['link']
        trackers = magnet_link.split("&tr=")[1:]
        try:
            season = item['season']
            episode = item['episode']
            availability = is_available(magnet_link, item['type'], item['season'] + item['episode'],
                                        config=config)
        except:
            season = None
            episode = None
            availability = is_available(magnet_link, item['type'], config=config)
        torrent_info = {
            "name": item['name'],
            "title": item['title'],
            "trackers": ["tracker:" + tracker for tracker in trackers],
            "magnet": magnet_link,
            "files": [],
            "hash": magnet_link.split("urn:btih:")[1].split("&")[0],
            "indexer": item['indexer'],
            "quality": item['quality'],
            "qualitySpec": item['qualitySpec'],
            "seeders": item['seeders'],
            "size": item['size'],
            "language": item['language'],
            "type": item['type'],
            "season": season,
            "episode": episode,
            "availability": availability
        }
        return torrent_info
    response = requests.get(item['link'])
    print("Getting torrent info")
    while response.status_code != 200:
        print("Retrying")
        response = requests.get(item['link'])
    print("Got torrent info")
    torrent = bencode.bdecode(response.content)
    trackers = []
    if 'announce-list' in torrent:
        for tracker in torrent['announce-list']:
            if len(tracker) > 0:
                trackers.append("tracker:" + tracker[0])
    if 'announce' in torrent:
        trackers.append("tracker:" + torrent['announce'])
    files = []
    if 'files' in torrent['info']:
        for file in torrent['info']['files']:
            if file['path'][-1].lower().endswith(tuple(format)):
                files.append(file['path'][-1])

    hash = hashlib.sha1(bencode.bencode(torrent['info'])).hexdigest()
    magnet = "magnet:?xt=urn:btih:" + hash + "&dn=" + torrent['info']['name'] + "&tr=" + "&tr=".join(trackers)
    try:
        season = item['season']
        episode = item['episode']
        availability = is_available(magnet, item['type'], item['season'] + item['episode'], config=config)
    except:
        season = None
        episode = None
        availability = is_available(magnet, item['type'], config=config)
    torrent_info = {
        "name": item['name'],
        "title": item['title'],
        "trackers": trackers,
        "magnet": magnet,
        "files": files,
        "hash": hash,
        "indexer": item['indexer'],
        "language": item['language'],
        "seeders": item['seeders'],
        "size": item['size'],
        "quality": item['quality'],
        "qualitySpec": item['qualitySpec'],
        "type": item['type'],
        "season": season,
        "episode": episode,
        "availability": availability

    }
    print("Returning torrent info")
    return torrent_info


def get_availability(torrent, config):
    if config is None:
        return None
    try:
        torrent_info = get_torrent_info(torrent, config)
        return torrent_info
    except:
        try:
            response = requests.get(torrent['link'], allow_redirects=False)
            if response.status_code == 302:
                magnet_link = response.headers['Location']
                trackers = magnet_link.split("&tr=")[1:]
                try:
                    season = torrent['season']
                    episode = torrent['episode']
                    availability = is_available(magnet_link, torrent['type'], torrent['season'] + torrent['episode'], config=config)
                except:
                    season = None
                    episode = None
                    availability = is_available(magnet_link, torrent['type'], config=config)
                torrent_info = {
                    "name": torrent['name'],
                    "title": torrent['title'],
                    "trackers": ["tracker:" + tracker for tracker in trackers],
                    "magnet": magnet_link,
                    "files": [],
                    "hash": magnet_link.split("urn:btih:")[1].split("&")[0],
                    "indexer": torrent['indexer'],
                    "quality": torrent['quality'],
                    "qualitySpec": torrent['qualitySpec'],
                    "seeders": torrent['seeders'],
                    "size": torrent['size'],
                    "language": torrent['language'],
                    "type": torrent['type'],
                    "season": season,
                    "episode": episode,
                    "availability": availability
                }
                return torrent_info
            else:
                print(f"Failed to get torrent info for {torrent['title']}")
                return None
        except:
            print(f"Failed to get torrent info for {torrent['title']}")
            return None


def availability(items, config):
    results = []
    items = items[:int(config['maxResults'])]
    with concurrent.futures.ThreadPoolExecutor(max_workers=int(config['maxResults'])) as executor:
        results = list(executor.map(lambda item: get_availability(item, config), items))
    return results

