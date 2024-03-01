import json

from utils.string_encoding import decodeb64


def parse_config(b64config):
    return json.loads(decodeb64(b64config))
