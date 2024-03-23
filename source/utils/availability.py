import base64
import concurrent.futures
import hashlib
import urllib.parse

import bencode
import requests

from utils.logger import setup_logger

logger = setup_logger(__name__)

format = {".mkv", ".mp4", ".avi", ".mov", ".flv", ".wmv", ".webm", ".mpg", ".mpeg", ".m4v", ".3gp", ".3g2", ".ogv",
          ".ogg", ".drc", ".gif", ".gifv", ".mng", ".avi", ".mov", ".qt", ".wmv", ".yuv", ".rm", ".rmvb", ".asf",
          ".amv", ".mp4", ".m4p", ".m4v", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".mpg", ".mpeg", ".m2v", ".m4v",
          ".svi", ".3gp", ".3g2", ".mxf", ".roq", ".nsv", ".flv", ".f4v", ".f4p", ".f4a", ".f4b"}

max_retries = 5


def get_torrent_info(item, debrid_service):
    if item.link.startswith("magnet:"):
        magnet_link = item.link
        trackers = magnet_link.split("&tr=")[1:]
        try:
            season = item.season
            episode = item.episode
            availability = debrid_service.get_availability(magnet_link, item.type, season + episode)
        except:
            season = None
            episode = None
            availability = debrid_service.get_availability(magnet_link, item.type)
        torrent_info = {
            "title": item.title,
            "trackers": ["tracker:" + tracker for tracker in trackers],
            "magnet": magnet_link,
            "files": [],
            "hash": magnet_link.split("urn:btih:")[1].split("&")[0],
            "indexer": item.indexer,
            "quality": item.quality,
            "qualitySpec": item.quality_spec,
            "seeders": item.seeders,
            "size": item.size,
            "language": item.language,
            "type": item.type,
            "season": season,
            "episode": episode,
            "availability": availability
        }
        return torrent_info
    response = requests.get(item.link)
    logger.info("Getting torrent info")
    attempts = 0
    while response.status_code != 200 and attempts < max_retries:
        logger.info("Retrying")
        response = requests.get(item.link)
        attempts += 1
    if response.status_code == 200:
        logger.info("Successfully retrieved torrent info")
    else:
        logger.error("Failed to retrieve torrent info after " + str(max_retries) + " attempts")
    logger.info("Got torrent info")
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
        season = item.season
        episode = item.episode
        availability = debrid_service.get_availability(magnet, item.type, season + episode)
    except:
        season = None
        episode = None
        availability = debrid_service.get_availability(magnet, item.type)
    torrent_info = {
        "title": item.title,
        "trackers": trackers,
        "magnet": magnet,
        "files": files,
        "hash": hash,
        "indexer": item.indexer,
        "language": item.language,
        "seeders": item.seeders,
        "size": item.size,
        "quality": item.quality,
        "qualitySpec": item.quality_spec,
        "type": item.type,
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
            response = requests.get(torrent.link, allow_redirects=False)
            if response.status_code == 302 or response.status_code == 200:
                if response.status_code == 302:
                    magnet_link = response.headers['Location']
                    logger.info(f"Got Magnet: {magnet_link}")
                else:
                    magnet_link = torrent_to_magnet(response.content)
                    logger.info(f"Got Magnet: {magnet_link}")
                url_parts = urllib.parse.urlparse(magnet_link)
                query_parts = urllib.parse.parse_qs(url_parts.query)
                logger.info(f"Query parts: {query_parts}")
                if 'tr' in query_parts:  # trackers
                    trackers = query_parts['tr']
                else:
                    trackers = []
                if response.status_code == 200:
                    logger.info(f"Got Tracker: {trackers}")
                # TODO: When get availability fails in try block, it retries in except block (why?)
                try:
                    season = torrent.season
                    episode = torrent.episode
                    availability = debrid_service.get_availability(magnet_link, torrent.type, season + episode)
                except:
                    season = None
                    episode = None
                    availability = debrid_service.get_availability(magnet_link, torrent.type)
                torrent_info = {
                    "title": torrent.title,
                    "trackers": ["tracker:" + tracker for tracker in trackers],
                    "magnet": magnet_link,
                    "files": [],
                    "hash": magnet_link.split("urn:btih:")[1].split("&")[0],
                    "indexer": torrent.quality_spec,
                    "quality": torrent.quality_spec,
                    "qualitySpec": torrent.quality_spec,
                    "seeders": torrent.seeders,
                    "size": torrent.size,
                    "language": torrent.language,
                    "type": torrent.type,
                    "season": season,
                    "episode": episode,
                    "availability": availability
                }
                return torrent_info
            else:
                logger.error(f"Failed to get torrent info for {torrent.title}")
                return None
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            logger.error(f"Failed to get torrent info for {torrent['title']}")
            return None


# https://github.com/DanySK/torrent2magnet/blob/master/torrent2magnet.py
def torrent_to_magnet(torrent_content):
    metadata = bencode.decode(torrent_content)
    subj = metadata['info']
    hash_content = bencode.encode(subj)
    digest = hashlib.sha1(hash_content).digest()
    b32hash = base64.b32encode(digest)
    magnet = 'magnet:?' \
             + 'xt=urn:btih:' + b32hash.decode() \
             + '&dn=' + metadata['info']['name']

    for tracker in metadata['announce-list']:
        magnet += '&tr=' + urllib.parse.quote_plus(tracker[0])

    length = max(metadata['info']['files'], key=lambda x: x['length'])['length']

    magnet += '&xl=' + str(length)
    return magnet


def availability(items, debrid_service, config):
    results = []
    items = items[:int(config['maxResults'])]
    with concurrent.futures.ThreadPoolExecutor(max_workers=int(config['maxResults'])) as executor:
        results = list(executor.map(lambda item: get_availability(item, debrid_service), items))
    return results
