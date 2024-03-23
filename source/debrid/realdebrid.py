import json
import time

import requests

from debrid.base_debrid import BaseDebrid
from utils.logger import setup_logger

logger = setup_logger(__name__)


class RealDebrid(BaseDebrid):
    def __init__(self, config):
        super().__init__(config)
        self.base_url = "https://api.real-debrid.com"
        self.headers = {"Authorization": f"Bearer {self.config['debridKey']}"}

    def add_magnet(self, magnet):
        url = f"{self.base_url}/rest/1.0/torrents/addMagnet"
        data = {"magnet": magnet}
        return self.get_json_response(url, method='post', headers=self.headers, data=data)

    def get_torrent_info(self, torrent_id):
        url = f"{self.base_url}/rest/1.0/torrents/info/{torrent_id}"
        return self.get_json_response(url, headers=self.headers)

    def select_files(self, torrent_id, file_id):
        url = f"{self.base_url}/rest/1.0/torrents/selectFiles/{torrent_id}"
        data = {"files": file_id}
        requests.post(url, headers=self.headers, data=data)

    def unrestrict_link(self, link):
        url = f"{self.base_url}/rest/1.0/unrestrict/link"
        data = {"link": link}
        return self.get_json_response(url, method='post', headers=self.headers, data=data)

    def is_already_added(self, magnet):
        hash = magnet.split("urn:btih:")[1].split("&")[0].lower()
        url = f"{self.base_url}/rest/1.0/torrents"
        torrents = self.get_json_response(url, headers=self.headers)
        for torrent in torrents:
            if torrent['hash'].lower() == hash:
                return torrent['id']
        return False

    def wait_for_link(self, torrent_id):
        while True:
            torrent_info = self.get_torrent_info(torrent_id)
            if torrent_info and 'links' in torrent_info:
                return torrent_info['links']
            time.sleep(5)

    def get_availability(self, magnet, stream_type, season_episode=None):
        hash = magnet.split("urn:btih:")[1].split("&")[0]
        logger.info(f"RealDebrid get availability for {stream_type} with hash: {hash}")
        url = f"{self.base_url}/rest/1.0/torrents/instantAvailability/" + hash
        logger.info(f"URL: {url}")
        data = self.get_json_response(url, headers=self.headers)
        results = next(iter(data.items()))[1]
        if len(results) == 0:
            return False
        if type == "movie":
            return True
        if type == "series":
            for result in results['rd']:
                for file in result.items():
                    if season_episode in file[1]['filename']:
                        return True
            return False
        return True

    def get_stream_link(self, query):
        query_details = json.loads(query)
        magnet = query_details['magnet']
        stream_type = query_details['type']

        logger.info(f"RealDebrid get stream link for {stream_type} with magnet: {magnet}")
        torrent_id = self.is_already_added(magnet)

        logger.info(f"Cached torrent ID: {torrent_id}")
        if not torrent_id:
            magnet_response = self.add_magnet(magnet)
            logger.info(f"RealDebrid add magnet response: {magnet_response}")
            if not magnet_response or 'id' not in magnet_response:
                return "Error: Failed to add magnet."
            torrent_id = magnet_response['id']
            logger.info(f"New torrent ID: {torrent_id}")

        logger.info(f"Getting torrent info for ID: {torrent_id}")
        torrent_info = self.get_torrent_info(torrent_id)
        if not torrent_info or 'files' not in torrent_info:
            return "Error: Failed to get torrent info."

        # Selecting files based on stream type, this is a simplified example
        if stream_type == "movie":
            logger.info("Selecting largest file for movie")
            # Assuming we select the largest file for movies
            largest_file_id = max(torrent_info['files'], key=lambda x: x['bytes'])['id']
            logger.info(f"Selected file ID: {largest_file_id}")
            self.select_files(torrent_id, str(largest_file_id))
        elif stream_type == "series":
            logger.info("Selecting file for series")
            season_episode = f"{query_details.get('season').lower()}{query_details.get('episode').lower()}"
            filtered_files = [file['id'] for file in torrent_info['files'] if season_episode in file['path'].lower()]
            if not filtered_files:
                return "Error: Episode file not found."
            logger.info(f"Filtered files: {filtered_files}")
            file_id = max(filtered_files, key=lambda x: x['bytes'])
            logger.info(f"Selected file ID: {file_id}")
            self.select_files(torrent_id, str(file_id))
        else:
            return "Error: Unsupported stream type."

        logger.info(f"Waiting for the link to be ready for torrent ID: {torrent_id}")
        # Waiting for the link to be ready
        download_link = self.wait_for_link(torrent_id)

        logger.info(f"Unrestricting the download link: {download_link}")
        # Unrestricting the download link
        unrestrict_response = self.unrestrict_link(download_link)
        if not unrestrict_response or 'download' not in unrestrict_response:
            return "Error: Failed to unrestrict link."

        logger.info(f"Got download link: {unrestrict_response['download']}")
        return unrestrict_response['download']
