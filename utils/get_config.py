import json


def get_config():
    try:
        with open('config.json') as json_file:
            data = json.load(json_file)
            return data
    except:
        return None


def set_config(data):
    with open('config.json', 'w') as json_file:
        json.dump(data, json_file)
