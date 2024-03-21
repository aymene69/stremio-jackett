import json

import requests

from constants import CACHER_URL, EXCLUDED_TRACKERS
from debrid.get_debrid_service import get_debrid_service
from utils.get_availability import get_availability
from utils.logger import setup_logger

logger = setup_logger(__name__)


def search_cache(media):
    logger.info("Searching for cached " + media.type + " results")
    url = CACHER_URL + "getResult/" + media.type + "/"
    # TODO: Wtf, why do we need to use __dict__ here? And also, why is it stuck when we use media directly?
    response = requests.get(url, json=media.__dict__)
    return response.json()


def cache_results(torrents, type, config):
    results = []
    for torrent in torrents:
        if torrent['indexer'] in EXCLUDED_TRACKERS:
            continue
        else:
            try:
                torrent_info = get_availability(torrent, get_debrid_service(config))
                if torrent_info is not None:
                    torrent_info['language'] = torrent['language']
                    torrent_info['quality'] = torrent['quality']
                    torrent_info['qualitySpec'] = torrent['qualitySpec']
                    torrent_info['seeders'] = torrent['seeders']
                    torrent_info['size'] = torrent['size']
                    if type == "movie":
                        torrent_info['year'] = torrent['year']
                    if type == "series":
                        torrent_info['season'] = torrent['season']
                        torrent_info['episode'] = torrent['episode']
                        torrent_info['seasonfile'] = torrent['seasonfile']
                    results.append(torrent_info)
            except:
                pass
    try:
        response = requests.post(CACHER_URL + "pushResult/" + type, data=json.dumps(results, indent=4, default=set_default))
        if response.status_code == 200:
            logger.info("Cached " + str(len(results)) + " " + type + " results")
        else:
            logger.error("Failed to cache " + type + " results: " + str(response))
    except:
        logger.exception("Failed to cache results")
        pass

def set_default(obj):
    if isinstance(obj, set):
        return list(obj)  # Convert set to list
    raise TypeError