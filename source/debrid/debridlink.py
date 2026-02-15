# debridlink.py
import hashlib
import json
from urllib.parse import unquote

from constants import NO_CACHE_VIDEO_URL
from debrid.base_debrid import BaseDebrid
from utils.general import get_info_hash_from_magnet, season_episode_in_filename
from utils.logger import setup_logger

logger = setup_logger(__name__)


class DebridLink(BaseDebrid):
    def __init__(self, config):
        super().__init__(config)
        self.base_url = "https://debrid-link.com/api/v2"
        self.api_key = self.config["debridKey"]
        self.ip = self.config.get("ip", "")

    def get_user_hash(self):
        return hashlib.md5(self.api_key.encode()).hexdigest()

    def get_stream_link(self, query_string, ip=None):
        query = json.loads(query_string)

        magnet = query["magnet"]
        stream_type = query["type"]
        file_index = (
            int(query["file_index"]) if query["file_index"] is not None else None
        )
        season = query["season"]
        episode = query["episode"]
        torrent_download = (
            unquote(query["torrent_download"])
            if query["torrent_download"] is not None
            else None
        )
        info_hash = get_info_hash_from_magnet(magnet)
        logger.info(
            f"DebridLink get stream link for {stream_type} with hash: {info_hash}"
        )

        # Add magnet or torrent file to Debrid-Link
        torrent_info = self._add_magnet_or_torrent(magnet, torrent_download, ip)
        if not torrent_info:
            return "Error: Failed to add torrent."

        # Get available files
        files = self._get_files_from_torrent(torrent_info)
        if not files:
            return NO_CACHE_VIDEO_URL

        # Find the appropriate file
        selected_file = self._select_file(
            files, stream_type, file_index, season, episode
        )
        if not selected_file:
            return NO_CACHE_VIDEO_URL

        if not selected_file.get("ready", False):
            logger.info("File is not ready yet.")
            return NO_CACHE_VIDEO_URL

        return selected_file["url"]

    def get_availability_bulk(self, hashes_or_magnets, ip=None):
        # Debrid-Link does not support cache check
        return dict()

    def add_magnet(self, magnet, ip=None):
        url = f"{self.base_url}/seedbox/add"
        headers = self._get_headers()
        body = {"url": magnet, "async": True, "ip": ip or self.ip}
        return self._request("POST", url, headers=headers, json=body)

    def add_torrent(self, torrent_file, ip=None):
        url = f"{self.base_url}/seedbox/add"
        headers = self._get_headers()
        files = {"file": ("file.torrent", torrent_file, "application/x-bittorrent")}
        data = {"ip": ip or self.ip}
        return self._request("POST", url, headers=headers, data=data, files=files)

    def get_torrent_info(self, torrent_id):
        url = f"{self.base_url}/seedbox/list"
        headers = self._get_headers()
        response = self._request("GET", url, headers=headers)
        if response and "value" in response:
            for torrent in response["value"]:
                if torrent["id"] == torrent_id:
                    return torrent
        return None

    def get_progress_torrents(self):
        url = f"{self.base_url}/seedbox/list"
        headers = self._get_headers()
        response = self._request("GET", url, headers=headers)
        if not response or "value" not in response:
            return {}

        progress = {}
        for torrent in response["value"]:
            progress[torrent.get("hashString", "")] = {
                "percent": torrent.get("downloadPercent", 0),
                "speed": torrent.get("downloadSpeed", 0),
            }
        return progress

    def _get_headers(self):
        return {
            "user-agent": "Stremio",
            "accept": "application/json",
            "authorization": f"Bearer {self.api_key}",
        }

    def _request(self, method, url, headers=None, json=None, data=None, files=None):
        params = {"ip": self.ip}
        if files:
            # For multipart/form-data, we need to handle differently
            response = self.get_json_response(
                url, method=method.lower(), headers=headers, data=data, files=files
            )
        elif json:
            import urllib.parse

            query_params = urllib.parse.urlencode(params)
            full_url = f"{url}?{query_params}"
            response = self.get_json_response(
                full_url, method=method.lower(), headers=headers, data=json
            )
        else:
            import urllib.parse

            query_params = urllib.parse.urlencode(params)
            full_url = f"{url}?{query_params}"
            response = self.get_json_response(
                full_url, method=method.lower(), headers=headers
            )

        if response is None:
            return None

        if not response.get("success", False):
            logger.error(f"DebridLink API error: {response}")
            self._handle_api_error(response.get("error", ""))

        return response

    def _handle_api_error(self, error_code):
        error_messages = {
            "badToken": "Api key expired",
            "maxLink": "You must be premium on debrid",
            "maxLinkHost": "You must be premium on debrid",
            "maxData": "You must be premium on debrid",
            "maxDataHost": "You must be premium on debrid",
            "maxTorrent": "You must be premium on debrid",
            "torrentTooBig": "You must be premium on debrid",
            "freeServerOverload": "You must be premium on debrid",
        }
        if error_code in error_messages:
            raise Exception(error_messages[error_code])
        raise Exception(f"Invalid Debrid-Link API result: {error_code}")

    def _add_magnet_or_torrent(self, magnet, torrent_download=None, ip=None):
        if torrent_download is None:
            logger.info("Adding magnet to Debrid-Link")
            response = self.add_magnet(magnet, ip)
            logger.info(f"Debrid-Link add magnet response: {response}")
        else:
            logger.info("Downloading torrent file from Jackett")
            torrent_file = self.donwload_torrent_file(torrent_download)
            logger.info("Torrent file downloaded from Jackett")

            logger.info("Adding torrent file to Debrid-Link")
            response = self.add_torrent(torrent_file, ip)
            logger.info(f"Debrid-Link add torrent file response: {response}")

        if (
            not response
            or not response.get("success", False)
            or "value" not in response
        ):
            return None

        return response["value"]

    def _get_files_from_torrent(self, torrent):
        if "files" not in torrent or len(torrent["files"]) == 0:
            return []

        files = []
        for index, file in enumerate(torrent["files"]):
            files.append(
                {
                    "name": file.get("name", ""),
                    "size": file.get("size", 0),
                    "id": f"{torrent['id']}:{index}",
                    "url": file.get("downloadUrl", ""),
                    "ready": file.get("downloadPercent", 0) == 100,
                }
            )
        return files

    def _select_file(self, files, stream_type, file_index, season, episode):
        if file_index is not None:
            for file in files:
                if file["id"].endswith(f":{file_index}"):
                    return file
            return None

        if stream_type == "movie":
            return max(files, key=lambda x: x["size"]) if files else None
        elif stream_type == "series":
            matching_files = []
            for file in files:
                if season_episode_in_filename(file["name"], season, episode):
                    matching_files.append(file)

            if len(matching_files) == 0:
                logger.error(f"No matching files for {season} {episode} in torrent.")
                return None

            return max(matching_files, key=lambda x: x["size"])

        return None
