import requests


def search_cache(query):
    print(query)
    print("Searching for cached movies on remote server")
    if query['type'] == "movie":
        url = "https://stremio-jackett-cacher.elfhosted.com/getResult/movie/"
        response = requests.get(url, json=query)
        return response.json()
    if query['type'] == "series":
        url = "https://stremio-jackett-cacher.elfhosted.com/getResult/series/"
        response = requests.get(url, json=query)
        return response.json()
