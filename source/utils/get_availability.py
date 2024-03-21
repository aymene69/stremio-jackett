import concurrent.futures
import hashlib

import bencode
import requests
import base64

from utils.logger import setup_logger

logger = setup_logger(__name__)

format = {".mkv", ".mp4", ".avi", ".mov", ".flv", ".wmv", ".webm", ".mpg", ".mpeg", ".m4v", ".3gp", ".3g2", ".ogv",
          ".ogg", ".drc", ".gif", ".gifv", ".mng", ".avi", ".mov", ".qt", ".wmv", ".yuv", ".rm", ".rmvb", ".asf",
          ".amv", ".mp4", ".m4p", ".m4v", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".mpg", ".mpeg", ".m2v", ".m4v",
          ".svi", ".3gp", ".3g2", ".mxf", ".roq", ".nsv", ".flv", ".f4v", ".f4p", ".f4a", ".f4b"}

max_retries = 5


def get_torrent_info(item, debrid_service):
    if item['link'].startswith("magnet:"):
        magnet_link = item['link']
        trackers = magnet_link.split("&tr=")[1:]
        try:
            season = item['season']
            episode = item['episode']
            availability = debrid_service.get_availability(magnet_link, item['type'], item['season'] + item['episode'])
        except:
            season = None
            episode = None
            availability = debrid_service.get_availability(magnet_link, item['type'])
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
    logger.info("Getting torrent info")
    attempts = 0
    while response.status_code != 200 and attempts < max_retries:
        logger.info("Retrying")
        response = requests.get(item['link'])
        attempts += 1
    if response.status_code == 200:
        logger.info("Successfully retrieved torrent info")
    else:
        logger.error("Failed to retrieve torrent info after " + str(max_retries) + " attempts")
    logger.info("Got torrent info")
    torrent = bencode.bdecode(response.content)

    trackers = set()
    if 'announce-list' in torrent:
        for tracker in torrent['announce-list']:
            if len(tracker) > 0:
                trackers.add("tracker:" + tracker[0])

    if 'announce' in torrent:
        #Some torrents have lists for these for some reason
        if isinstance(torrent['announce'], list):
            for tracker in torrent['announce']:
                trackers.add("tracker:" + tracker)
        else:
            trackers.add("tracker:" + torrent['announce'])

    files = []
    if 'files' in torrent['info']:
        for file in torrent['info']['files']:
            if file['path'][-1].lower().endswith(tuple(format)):
                files.append(file['path'][-1])
    
    # BitTorrent info hash (BTIH)
    # These are hex-encoded SHA-1 hash sums of the "info" sections of BitTorrent metafiles as used by   BitTorrent to identify downloadable files or sets of files. For backwards compatibility with existing links, clients should also support the Base32 encoded version of the hash.[3]
    # xt=urn:btih:[ BitTorrent Info Hash (Hex) ]
    # Some clients require Base32 of info_hash

    hashcontents = bencode.bencode(torrent['info'])
    base32Hash = base64.b32encode(hashlib.sha1(hashcontents).digest()).decode()
    hash = hexHash = hashlib.sha1(hashcontents).hexdigest()

    magnet = hexMagnet = f"magnet:?xt=urn:btih:{hexHash}&dn={torrent['info']['name']}&tr={'&tr='.join(trackers) if trackers else ''}"
    base32Magnet = f"magnet:?xt=urn:btih:{base32Hash}&dn={torrent['info']['name']}&tr={'&tr='.join(trackers) if trackers else ''}"

    if not debrid_service.is_valid_magnet(magnet):
        magnet = base32Magnet
        hash = base32Hash

    try:
        season = item['season']
        episode = item['episode']
        availability = debrid_service.get_availability(magnet, item['type'], item['season'] + item['episode'])
    except:
        season = None
        episode = None
        availability = debrid_service.get_availability(magnet, item['type'])
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
    logger.info("Returning torrent info")
    return torrent_info


def get_availability(torrent, debrid_service):
    try:
        torrent_info = get_torrent_info(torrent, debrid_service)
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
                    availability = debrid_service.get_availability(magnet_link, torrent['type'], torrent['season'] + torrent['episode'])
                except:
                    season = None
                    episode = None
                    availability = debrid_service.get_availability(magnet_link, torrent['type'])
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
                logger.error(f"Failed to get torrent info for {torrent['title']}")
                return None
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            logger.error(f"Failed to get torrent info for {torrent['title']}")
            return None


def availability(items, debrid_service, config):
    results = []
    items = items[:int(config['maxResults'])]
    with concurrent.futures.ThreadPoolExecutor(max_workers=int(config['maxResults'])) as executor:
        results = list(executor.map(lambda item: get_availability(item, debrid_service), items))
    return results
