import json

import requests

from constants import NO_RESULTS, JACKETT_ERROR, NO_CONFIG
from utils.logger import setup_logger
from utils.parse_xml import parse_xml

logger = setup_logger(__name__)


def search(query, config):
    if config is None:
        return NO_CONFIG

    logger.info("Started Jackett search for " + query['type'] + " " + query['title'])

    if query['type'] == "movie":

        url = (f"{config['jackettHost']}/api/v2.0/indexers/all/results/torznab/api?apikey={config['jackettApiKey']}"
               f"&t=movie&cat=2000&q={query['title']}&year={query['year']}")
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = parse_xml(response.text, {"type": "movie", "year": query['year']}, config=config)
            if data:
                return json.loads(data)
            else:
                return NO_RESULTS
        except requests.exceptions.RequestException as e:
            logger.error(e)
            return []
    elif query['type'] == "series":
        url_ep = (f"{config['jackettHost']}/api/v2.0/indexers/all/results/torznab/api?apikey={config['jackettApiKey']}"
                  f"&t=tvsearch&cat=5000&q={query['title']}&season={str(int(query['season'].replace('S','')))}"
                  f"&ep={str(int(query['episode'].replace('E','')))}")
        url_season = (
            f"{config['jackettHost']}/api/v2.0/indexers/all/results/torznab/api?apikey={config['jackettApiKey']}"
            f"&t=tvsearch&cat=5000&q={query['title']}&season={str(int(query['season'].replace('S','')))}")
        try:
            response_ep = requests.get(url_ep)
            response_ep.raise_for_status()
            response_season = requests.get(url_season)
            response_season.raise_for_status()

            data_ep = parse_xml(response_ep.text,
                                {"type": "series", "season": query['season'], "episode": query['episode'],
                                 "seasonfile": False}, config=config)
            data_season = parse_xml(response_season.text,
                                    {"type": "series", "season": query['season'], "episode": query['episode'],
                                     "seasonfile": True}, config=config)
            data = json.dumps(json.loads(data_ep) + json.loads(data_season), indent=4)          
            if data:
                return json.loads(data)
            else:
                return NO_RESULTS
        except requests.exceptions.RequestException as e:
            logger.error(e)
            return []
