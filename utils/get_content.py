import requests

from utils.logger import setup_logger

logger = setup_logger(__name__)


def get_name(id, type, config):
    logger.info("Getting metadata for " + type + " with id " + id)

    if type == "movie":
        full_id = id.split(":")
        url = f"https://api.themoviedb.org/3/find/{full_id[0]}?api_key={config['tmdbApi']}&external_source=imdb_id&language={config['language']}"
        response = requests.get(url)
        data = response.json()
        result = {
            "title": data["movie_results"][0]["title"],
            "year": data["movie_results"][0]["release_date"][:4],
            "type": "movie",
            "language": config['language']
        }
        logger.info("Got metadata for " + type + " with id " + id)
        return result
    else:
        full_id = id.split(":")
        url = f"https://api.themoviedb.org/3/find/{full_id[0]}?api_key={config['tmdbApi']}&external_source=imdb_id&language={config['language']}"
        response = requests.get(url)
        data = response.json()
        result = {
            "title": data["tv_results"][0]["name"],
            "season": "S{:02d}".format(int(full_id[1])),
            "episode": "E{:02d}".format(int(full_id[2])),
            "type": "series",
            "language": config['language']
        }
        logger.info("Got metadata for " + type + " with id " + id)
        return result
