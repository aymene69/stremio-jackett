import time

import requests

from utils.logger import setup_logger


class BaseDebrid:
    def __init__(self, config):
        self.config = config
        self.logger = setup_logger(__name__)

    def get_json_response(self, url, method='get', data=None, headers=None):
        if method == 'get':
            response = requests.get(url, headers=headers)
        elif method == 'post':
            response = requests.post(url, data=data, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        if response.status_code == 200:
            return response.json()
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