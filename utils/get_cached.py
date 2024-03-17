import requests

from constants import CACHER_URL
from utils.logger import setup_logger
from utils.filter_results import filter_items
from utils.process_results import process_results

logger = setup_logger(__name__)

def search_cache(query):
    logger.info(query)
    logger.info("Searching for cached " + query['type'] + " results")

    url = CACHER_URL + "getResult/" + query['type'] + "/"
    response = requests.get(url, json=query)

    return response.json()

def get_cached_results(name, stream_type, config):
    logger.info("Getting cached results")
    cached_results = search_cache(name)

    logger.info("Got " + str(len(cached_results)) + " cached results")
    logger.info("Filtering cached results")
    filtered_cached_results = filter_items(cached_results,
                                           stream_type,
                                           config=config,
                                           cached=True,
                                           season=name['season'] if stream_type == "series" else None,
                                           episode=name['episode'] if stream_type == "series" else None)

    logger.info("Filtered cached results")
    return filtered_cached_results

def process_cached_results(filtered_cached_results, stream_type, name, config):
    logger.info("Cached results found")
    logger.info("Processing cached results")
    
    stream_list = process_results(filtered_cached_results[:int(config['maxResults'])],
                                  True,
                                  stream_type,
                                  name['season'] if stream_type == "series" else None,
                                  name['episode'] if stream_type == "series" else None,
                                  config=config)
    
    logger.info("Processed cached results")
    if len(stream_list) == 0:
        logger.info("No results found")
        return None
    
    return {"streams": stream_list}

