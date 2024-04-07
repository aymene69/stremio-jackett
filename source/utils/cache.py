import json
from typing import List

import requests

from constants import CACHER_URL, EXCLUDED_TRACKERS
from torrent.torrent_item import TorrentItem
from utils.logger import setup_logger

logger = setup_logger(__name__)


def search_cache(media):
    logger.info("Searching for cached " + media.type + " results")
    url = CACHER_URL + "getResult/" + media.type + "/"
    # Without that, the cache doesn't return results. Maybe make multiple requests? One for each language, just like jackett?
    cache_search = media.__dict__
    cache_search['title'] = cache_search['titles'][0]
    cache_search['language'] = cache_search['languages'][0]
    # TODO: Wtf, why do we need to use __dict__ here? And also, why is it stuck when we use media directly?
    response = requests.get(url, json=cache_search)
    return response.json()


def cache_results(torrents: List[TorrentItem], media):
    logger.info("Started caching results")

    cache_items = []
    for torrent in torrents:
        if torrent.indexer in EXCLUDED_TRACKERS:
            continue

        try:
            cache_item = dict()

            cache_item['title'] = torrent.title
            cache_item['trackers'] = "tracker:".join(torrent.trackers)
            cache_item['magnet'] = torrent.magnet
            cache_item['files'] = []  # I guess keep it empty?
            cache_item['hash'] = torrent.info_hash
            cache_item['indexer'] = torrent.indexer
            cache_item['quality'] = torrent.quality
            cache_item['qualitySpec'] = ";".join(torrent.quality_spec)
            cache_item['seeders'] = torrent.seeders
            cache_item['size'] = torrent.size
            cache_item['language'] = ";".join(torrent.languages)
            cache_item['type'] = media.type
            cache_item['availability'] = torrent.availability

            if media.type == "movie":
                cache_item['year'] = media.year
            elif media.type == "series":
                cache_item['season'] = media.season
                cache_item['episode'] = media.episode
                cache_item['seasonfile'] = False  # I guess keep it false to not mess up results?

            cache_items.append(cache_item)
        except:
            logger.exception("An exception occured durring cache parsing")
            pass
    try:
        url = f"{CACHER_URL}pushResult/{media.type}"
        cache_data = json.dumps(cache_items, indent=4)
        response = requests.post(url, data=cache_data)
        response.raise_for_status()

        if response.status_code == 200:
            logger.info(f"Cached {str(len(cache_items))} {media.type} results")
        else:
            logger.error(f"Failed to cache {media.type} results: {str(response)}")
    except:
        logger.error("Failed to cache results")
        pass
