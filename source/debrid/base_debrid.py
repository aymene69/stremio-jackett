import time

import requests

from utils.logger import setup_logger


class BaseDebrid:
    def __init__(self, config):
        self.config = config
        self.logger = setup_logger(__name__)

    def get_response(self, url, method='get', data=None, headers=None):
        if method == 'get':
            return requests.get(url, headers=headers)
        elif method == 'post':
            return requests.post(url, data=data, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

    def get_json_response(self, url, method='get', data=None, headers=None):
        if method == 'get':
            response = requests.get(url, headers=headers)
        elif method == 'post':
            response = requests.post(url, data=data, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        # Check if the request was successful
        if response.ok:
            try:
                return response.json()
            except ValueError:
                self.logger.error(f"Failed to parse response as JSON: {response.text}")
                return None
        else:
            self.logger.error(f"Request failed with status code {response.status_code}")
            return None

    def wait_for_ready_status(self, check_status_func, timeout=60, interval=5):
        start_time = time.time()
        while time.time() - start_time < timeout:
            if check_status_func():
                return True
            time.sleep(interval)
        return False
    
    def get_stream_link(self, query):
        raise NotImplementedError

    def add_magnet(self, magnet):
        raise NotImplementedError

    def get_availability(self, stream, stream_type, season_episode=None):
        raise NotImplementedError
    
    def is_valid_magnet(self, magnet):
        raise NotImplementedError
