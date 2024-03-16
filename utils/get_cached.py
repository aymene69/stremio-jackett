import requests

from constants import CACHER_URL
from utils.logger import setup_logger

logger = setup_logger(__name__)

#TODO: Caching does not work with direct torrenting
def search_cache(query):
    logger.info(query)
    logger.info("Searching for cached " + query['type'] + " results")
    url = CACHER_URL + "getResult/" + query['type'] + "/"
    response = requests.get(url, json=query)
    return response.json()
