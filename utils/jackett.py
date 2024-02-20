import requests
import json
from utils.parse_xml import parse_xml

host = "https://jackett.aymene.tech"
api = "8zhy2rf8djop7g4qh4xv5zr3mnqfxtr8"
type = "movie"
title = "Reacher"
year = "2023"

no_config = {'streams': [{'url': "#", 'title': "No configuration found"}]}
no_results = {'streams': [{'url': "#", 'title': "No results found"}]}
error = {'streams': [{'url': "#", 'title': "An error occured"}]}


def search(query, config):
    if config is None:
        return no_config

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
                return no_results
        except requests.exceptions.RequestException as e:
            return error
    elif query['type'] == "series":
        url_ep = (f"{config['jackettHost']}/api/v2.0/indexers/all/results/torznab/api?apikey={config['jackettApiKey']}"
                  f"&t=tvsearch&cat=5000&q={query['title']}+{query['season']}{query['episode']}")
        url_season = (f"{config['jackettHost']}/api/v2.0/indexers/all/results/torznab/api?apikey={config['jackettApiKey']}"
                      f"&t=tvsearch&cat=5000&q={query['title']}+{query['season']}")
        try:
            response_ep = requests.get(url_ep)
            response_ep.raise_for_status()
            response_season = requests.get(url_season)
            response_season.raise_for_status()
            data_ep = parse_xml(response_ep.text, {"type": "series", "season": query['season'], "episode": query['episode'], "seasonfile": False}, config=config)
            data_season = parse_xml(response_season.text, {"type": "series", "season": query['season'], "episode": query['episode'],"seasonfile": True}, config=config)
            data = json.dumps(json.loads(data_ep) + json.loads(data_season), indent=4)
            if data:
                return json.loads(data)
            else:
                return no_results
        except requests.exceptions.RequestException as e:
            return error
