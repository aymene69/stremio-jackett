import json

import requests

from constants import CACHER_URL
from utils.logger import setup_logger

logger = setup_logger(__name__)


def search_cache(media):
    logger.info("Searching for cached " + media.type + " results")
    url = CACHER_URL + "getResult/" + media.type + "/"
    # TODO: Wtf, why do we need to use __dict__ here? And also, why is it stuck when we use media directly?
    response = requests.get(url, json=media.__dict__)
    return response.json()
