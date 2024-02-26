import requests

from constants import CACHER_URL
from utils.logger import setup_logger

logger = setup_logger(__name__)


def search_cache(query):
    logger.info(query)
    logger.info("Searching for cached movies on remote server")
    if query['type'] == "movie":
        url = CACHER_URL + "getResult/movie/"
        response = requests.get(url, json=query)
        return response.json()
    if query['type'] == "series":
        url = CACHER_URL + "getResult/series/"
        response = requests.get(url, json=query)
        return response.json()
