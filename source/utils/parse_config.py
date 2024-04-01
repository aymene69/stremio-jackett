import json

from utils.string_encoding import decodeb64


def parse_config(b64config):
    config = json.loads(decodeb64(b64config))

    # For backwards compatibility
    if "languages" not in config:
        config["languages"] = [config["language"]]

    return config
