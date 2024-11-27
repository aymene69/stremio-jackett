# alldebrid.py
import json
import uuid
from urllib.parse import unquote

from constants import NO_CACHE_VIDEO_URL
from debrid.base_debrid import BaseDebrid
from utils.general import season_episode_in_filename
from utils.logger import setup_logger

logger = setup_logger(__name__)


class AllDebrid(BaseDebrid):
    def __init__(self, config):
        super().__init__(config)
        self.base_url = "https://api.alldebrid.com/v4.1/"

    def add_magnet(self, magnet, ip):
        url = f"{self.base_url}magnet/upload?agent=jackett&apikey={self.config['debridKey']}&magnet={magnet}&ip={ip}"
        return self.get_json_response(url)

    def add_torrent(self, torrent_file, ip):
        url = f"{self.base_url}magnet/upload/file?agent=jackett&apikey={self.config['debridKey']}&ip={ip}"
        files = {"files[0]": (str(uuid.uuid4()) + ".torrent", torrent_file, 'application/x-bittorrent')}
        return self.get_json_response(url, method='post', files=files)

    def check_magnet_status(self, id, ip):
        url = f"{self.base_url}magnet/status?agent=jackett&apikey={self.config['debridKey']}&id={id}&ip={ip}"
        return self.get_json_response(url)

    def unrestrict_link(self, link, ip):
        url = f"{self.base_url}link/unlock?agent=jackett&apikey={self.config['debridKey']}&link={link}&ip={ip}"
        return self.get_json_response(url)

    def get_stream_link(self, query_string, ip):
        query = json.loads(query_string)

        magnet = query['magnet']
        stream_type = query['type']
        torrent_download = unquote(query["torrent_download"]) if query["torrent_download"] is not None else None

        torrent_id = self.__add_magnet_or_torrent(magnet, torrent_download, ip)
        logger.info(f"Torrent ID: {torrent_id}")

        if not self.wait_for_ready_status(
                lambda: self.check_magnet_status(torrent_id, ip)["data"]["magnets"]["status"] == "Ready"):
            logger.error("Torrent not ready, caching in progress.")
            return NO_CACHE_VIDEO_URL
        logger.info("Torrent is ready.")

        logger.info(f"Getting data for torrent id: {torrent_id}")
        data = self.check_magnet_status(torrent_id, ip)["data"]
        logger.info(f"Retrieved data for torrent id")

        link = NO_CACHE_VIDEO_URL
        if stream_type == "movie":
            logger.info("Getting link for movie")
            link = data["magnets"]["files"][0]['l']
        elif stream_type == "series":
            season = query['season']
            episode = query['episode']
            logger.info(f"Getting link for series {season}, {episode}")
            strict_matching_files = []
            matching_files = []
            rank = 0
            if 'e' in data["magnets"]["files"][0].keys():
                for file in data["magnets"]["files"][0]["e"]:
                    if season_episode_in_filename(file["n"], season, episode, strict=True):
                        strict_matching_files.append(file)
                    elif season_episode_in_filename(file["n"], season, episode, strict=False):
                        matching_files.append(file)
                    rank += 1
            else:
                for file in data["magnets"]["files"]:
                    if season_episode_in_filename(file["n"], season, episode, strict=True):
                        strict_matching_files.append(file)
                    elif season_episode_in_filename(file["n"], season, episode, strict=False):
                        matching_files.append(file)
                    rank += 1

            if len(matching_files) == 0:
                logger.error(f"No matching files for {season} {episode} in torrent.")
                return f"Error: No matching files for {season} {episode} in torrent."

            link = max(matching_files, key=lambda x: x["s"])["l"]
        else:
            logger.error("Unsupported stream type.")
            return "Error: Unsupported stream type."

        if link == NO_CACHE_VIDEO_URL:
            return link

        logger.info(f"Alldebrid link: {link}")

        unlocked_link_data = self.unrestrict_link(link, ip)

        if not unlocked_link_data:
            logger.error("Failed to unlock link.")
            return "Error: Failed to unlock link."

        logger.info(f"Unrestricted link: {unlocked_link_data['data']['link']}")

        return unlocked_link_data["data"]["link"]

    def get_availability_bulk(self, hashes_or_magnets, ip=None):
        torrents = f"{self.base_url}magnet/status?agent=jackett&apikey={self.config['debridKey']}&ip={ip}"
        ids = []
        for element in self.get_json_response(torrents)["data"]["magnets"]:
            if element["hash"] in hashes_or_magnets:
                ids.append(element["id"])

        # if len(hashes_or_magnets) == 0:
        #     logger.info("No hashes to be sent to All-Debrid.")
        #     return dict()
        #
        # url = f"{self.base_url}magnet/instant?agent=jackett&apikey={self.config['debridKey']}&magnets[]={'&magnets[]='.join(hashes_or_magnets)}&ip={ip}"
        # print(url)
        # return self.get_json_response(url)


    def __add_magnet_or_torrent(self, magnet, torrent_download=None, ip=None):
        torrent_id = ""
        if torrent_download is None:
            logger.info(f"Adding magnet to AllDebrid")
            magnet_response = self.add_magnet(magnet, ip)
            logger.info(f"AllDebrid add magnet response: {magnet_response}")

            if not magnet_response or "status" not in magnet_response or magnet_response["status"] != "success":
                return "Error: Failed to add magnet."

            torrent_id = magnet_response["data"]["magnets"][0]["id"]
        else:
            logger.info(f"Downloading torrent file from Jackett")
            torrent_file = self.donwload_torrent_file(torrent_download)
            logger.info(f"Torrent file downloaded from Jackett")

            logger.info(f"Adding torrent file to AllDebrid")
            upload_response = self.add_torrent(torrent_file, ip)
            logger.info(f"AllDebrid add torrent file response: {upload_response}")

            if not upload_response or "status" not in upload_response or upload_response["status"] != "success":
                return "Error: Failed to add torrent file."

            torrent_id = upload_response["data"]["files"][0]["id"]

        logger.info(f"New torrent ID: {torrent_id}")
        return torrent_id
