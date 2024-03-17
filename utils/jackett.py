import json

import requests

from constants import NO_RESULTS, JACKETT_ERROR, NO_CONFIG
from utils.logger import setup_logger
from utils.parse_xml import parse_xml

logger = setup_logger(__name__)


def search(query, config):
    if config is None:
        logger.debug('No config!')
        return []
    
    logger.info("Started Jackett search for " + query['type'] + " " + query['title'])
    if query['type'] == "movie":
        return search_movie(query, config)
    elif query['type'] == "series":
        return search_series(query, config)

def search_movie(query, config):
    url = (f"{config['jackettHost']}/api/v2.0/indexers/all/results/torznab/api?apikey={config['jackettApiKey']}"
           f"&t=movie&cat=2000&q={query['title']}&year={query['year']}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        
        data = parse_xml(response.text,
                         {"type": "movie",
                          "year": query['year']},
                         config)
        if data:
            return json.loads(data)
        else:
            return []
    except requests.exceptions.RequestException as e:
        logger.error('An error occured durring Jackett request: %s', 'division', exc_info=e)
        return []

def search_series(query, config):
    season = str(int(query['season'].replace('S','')))
    episode = str(int(query['episode'].replace('E','')))

    url_ep = (f"{config['jackettHost']}/api/v2.0/indexers/all/results/torznab/api?apikey={config['jackettApiKey']}"
              f"&t=tvsearch&cat=5000&q={query['title']}&season={season}"
              f"&ep={episode}")
    url_season = (
        f"{config['jackettHost']}/api/v2.0/indexers/all/results/torznab/api?apikey={config['jackettApiKey']}"
        f"&t=tvsearch&cat=5000&q={query['title']}&season={season}")

    try:
        # Main query
        response_ep = requests.get(url_ep)
        response_ep.raise_for_status()
        response_season = requests.get(url_season)
        response_season.raise_for_status()

        data_ep = parse_xml(response_ep.text,
                            {"type": "series",
                            "season": query['season'],
                            "episode": query['episode'],
                            "seasonfile": False},
                            config)
        
        data_season = parse_xml(response_season.text,
                                {"type": "series",
                                "season": query['season'],
                                "episode": query['episode'],
                                "seasonfile": True},
                                config)
        
        merged_data = json.dumps(json.loads(data_ep) + json.loads(data_season), indent=4)
        
        if merged_data and merged_data != '[]':
            return json.loads(merged_data)
        
        # Fallback query
        logger.info("Fallback series query")
        url_title = (
            f"{config['jackettHost']}/api/v2.0/indexers/all/results/torznab/api?apikey={config['jackettApiKey']}"
            f"&t=tvsearch&cat=5000&q={query['title']}")
        
        response_title = requests.get(url_title)
        response_title.raise_for_status()
        
        fallback_data = parse_xml(response_title.text,
                                  {"type": "series",
                                  "season": query['season'],
                                  "episode": query['episode'],
                                  "seasonfile": True},
                                 config)
        if fallback_data:
            return json.loads(fallback_data)
        else:
            return []
    except requests.exceptions.RequestException as e:
        logger.error('An error occured durring Jackett request: %s', 'division', exc_info=e)
        return []
