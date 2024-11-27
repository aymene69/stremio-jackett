import json
import requests
import time
from urllib.parse import unquote

from constants import NO_CACHE_VIDEO_URL
from debrid.base_debrid import BaseDebrid
from utils.general import season_episode_in_filename
from utils.logger import setup_logger

logger = setup_logger(__name__)


class TorBox(BaseDebrid):
    def __init__(self, config):
        super().__init__(config)
        self.base_url = "https://api.torbox.app/v1/api/"
        self.headers = {
            "Authorization": f"Bearer {self.config['debridKey']}",
        }

    def wait_for_files(self, torrent_hash, timeout=30, interval=5):
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.check_magnet_status(torrent_hash)
            if status:
                logger.info(f"Torrent status: {status}")
                if isinstance(status, list) and len(status) > 0 and "files" in status[0]:
                    files = status[0]["files"]
                    if files:
                        logger.info(f"Files are ready: {files}")
                        return files
            logger.info("Files not ready yet, retrying...")
            time.sleep(interval)
        logger.error("Timeout while waiting for torrent files.")
        return None

    def add_magnet(self, magnet):
        url = f"{self.base_url}torrents/createtorrent"
        data = {
            "magnet": magnet,
            "seed": 2
        }
        logger.info(f"URL: {url}")
        logger.info(f"Headers: {self.headers}")
        logger.info(f"Form Data: {data}")

        response = self.get_json_response(url, method="post", data=data)
        if response and response.get("success", False):
            data = response.get("data", {})
            if "torrent_id" not in data:
                logger.error(f"Missing 'torrent_id' in response: {response}")
                return None
            cached = "Found Cached Torrent" in response.get("detail", "")
            return {
                "torrent_id": data["torrent_id"],
                "hash": data["hash"],
                "is_cached": cached
            }
        else:
            logger.error(f"Failed to add magnet: {response}")
            return None

    def check_magnet_status(self, torrent_hash):
        url = f"{self.base_url}torrents/checkcached?hash={torrent_hash}&format=object&list_files=true"
        response = self.get_json_response(url)
        logger.info(f"Response from check_magnet_status: {response}")
        if response and response.get("success", False):
            return response["data"] if response["data"] else []
        else:
            logger.error(f"Failed to check status for hash {torrent_hash}: {response}")
            return None

    def get_file_download_link(self, torrent_id, file_name):
        url = f"{self.base_url}torrents/requestdl?token={self.config['debridKey']}&torrent_id={torrent_id}&file_id={file_name}&zip_link=false&torrent_file=false"
        response = self.get_json_response(url, method='get')
        if response and response.get("success", False):
            return response["data"]
        else:
            logger.error(f"Failed to get download link for torrent_id {torrent_id} and file {file_name}: {response}")
            return None

    def __add_magnet_or_torrent(self, magnet, torrent_download=None):
        torrent_id = None
        if magnet:
            logger.info(f"Adding magnet to TorBox")
            torrent_id = self.add_magnet(magnet)
            logger.info(f"TorBox add magnet response: {torrent_id}")
        else:
            logger.error("Only magnet links are supported for TorBox.")
        return torrent_id

    def get_stream_link(self, query_string, ip):
        query = json.loads(query_string)
        magnet = query["magnet"]
        stream_type = query["type"]
        season = query.get("season")
        episode = query.get("episode")

        magnet_data = self.add_magnet(magnet)
        if not magnet_data:
            logger.error("Failed to add magnet or retrieve torrent_id.")
            return NO_CACHE_VIDEO_URL

        torrent_id = magnet_data.get("torrent_id")
        if not torrent_id:
            logger.error("Missing torrent_id in magnet_data.")
            return NO_CACHE_VIDEO_URL

        is_cached = magnet_data["is_cached"]

        if is_cached:
            logger.info("Magnet is already cached. Files are ready.")
            files = self.check_magnet_status(magnet_data["hash"])[magnet_data["hash"]]
            if not files or "files" not in files:
                logger.error("Files not found in cached torrent.")
                return NO_CACHE_VIDEO_URL
        else:
            files = self.wait_for_files(magnet_data["hash"])
            if not files:
                logger.error(f"No files found for magnet {magnet}.")
                return NO_CACHE_VIDEO_URL

        if stream_type == "movie":
            largest_file_index, largest_file = max(
                enumerate(files["files"]), key=lambda x: x[1]["size"]
            )
            return self.get_file_download_link(torrent_id, largest_file_index)
        elif stream_type == "series":
            files = files["files"]
            matching_files = [
                (index, file) for index, file in enumerate(files)
                if season_episode_in_filename(file["name"], season, episode)
            ]
            if matching_files:
                selected_index, selected_file = max(
                    matching_files, key=lambda x: x[1]["size"]
                )
                return self.get_file_download_link(torrent_id, selected_index)
            else:
                logger.error(f"No matching files found for {season}x{episode}.")
                return NO_CACHE_VIDEO_URL
        else:
            logger.error("Unsupported stream type.")
            return "Error: Unsupported stream type."

    def get_json_response(self, url, method='get', **kwargs):
        try:
            if method == 'get':
                response = requests.get(url, headers=self.headers, **kwargs)
            elif method == 'post':
                response = requests.post(url, headers=self.headers, **kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            return None

    def get_availability_bulk(self, hashes_or_magnets, ip=None):

        available_torrents = {}

        for torrent_hash in hashes_or_magnets:
            url = f"{self.base_url}torrents/checkcached?hash={torrent_hash}&format=list&list_files=true"
            try:
                response = self.get_json_response(url)
                if response.get("success") and response.get("data"):
                    torrent_data = response["data"][0]
                    available_torrents[torrent_hash] = {
                        "name": torrent_data["name"],
                        "size": torrent_data["size"],
                        "files": torrent_data["files"]
                    }
                else:
                    self.logger.warning(f"Torrent {torrent_hash} is not cached or invalid response: {response}")

            except Exception as e:
                self.logger.error(f"Error while checking availability for hash {torrent_hash}: {e}")
                continue

        return available_torrents
