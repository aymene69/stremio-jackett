import requests
import hashlib
import bencode
import urllib.parse

from utils.logger import setup_logger
from typing import List


from torrent.torrent_item import TorrentItem
from jackett.jackett_result import JackettResult

class TorrentService:
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.__session = requests.Session()

    def convert_and_process(self, results: List[JackettResult]):
        torrent_items: List[TorrentItem] = []

        for result in results:
            torrent_item = result.convert_to_torrent_item()

            if torrent_item.link.startswith("magnet:"):
                self.__process_magnet(torrent_item)
            else:
                self.__process_web_url(torrent_item)

            torrent_items.append(torrent_item)
        
        return torrent_items

    def __process_web_url(self, result: TorrentItem):
        response = self.__session.get(result.link, allow_redirects=False)

        if response.status_code == 200:
            self.__process_torrent(result, response.content)
        elif response.status_code == 302:
            self.__process_magnet(response.headers['Location'])
        else:
            self.logger.error(f"Error code {response.status_code} while processing url: {result.link}")

    def __process_torrent(self, result: TorrentItem, torrent_file):
        metadata = bencode.bdecode(torrent_file)
        
        result.torrent = torrent_file
        result.trackers = self.__get_trackers_from_torrent(metadata)
        result.info_hash = self.__convert_torrent_to_hash(metadata["info"])
        result.magnet = self.__build_magnet(result.info_hash, metadata["info"]["name"], result.trackers)

    def __process_magnet(self, result: TorrentItem):
        if result.magnet is None:
            result.magnet = result.link

        if result.info_hash is None:
            result.info_hash = self.__get_info_hash_from_magnet(result.magnet)

        result.trackers = self.__get_trackers_from_magnet(result.magnet)

    def __convert_torrent_to_hash(self, torrent_contents):
        hashcontents = bencode.bencode(torrent_contents)
        hexHash = hashlib.sha1(hashcontents).hexdigest()
        return hexHash

    def __build_magnet(self, hash, display_name, trackers):
        magnet_base = "magnet:?xt=urn:btih:"
        magnet = f"{magnet_base}{hash}&dn={display_name}"

        if len(trackers) > 0:
            magnet = f"{magnet}&tr={"&tr=".join(trackers)}"
        
        return magnet


    def __get_info_hash_from_magnet(self, magnet: str):
        exact_topic_index = magnet.find("xt=")
        if exact_topic_index == -1:
            self.logger.debug(f"No exact topic in magnet {magnet}")
            return None
        
        exact_topic_substring = magnet[exact_topic_index:]
        end_of_exact_topic = exact_topic_substring.find("&")

        if end_of_exact_topic != -1:
            exact_topic_substring = exact_topic_substring[:end_of_exact_topic]

        info_hash = exact_topic_substring[exact_topic_substring.rfind(":")+1:]

        return info_hash
    
    def __get_trackers_from_torrent(self, torrent_metadata):
        # Sometimes list, sometimes string
        announce = torrent_metadata["announce"] if "announce" in torrent_metadata else [] 
        # Sometimes 2D array, sometimes 1D array
        announce_list = torrent_metadata["announce-list"] if "announce-list" in torrent_metadata else []  

        trackers = set()
        if isinstance(announce, str):
            trackers.add(announce)
        elif isinstance(announce, list):
            for tracker in announce:
                trackers.add(tracker)
        
        for announce_list_item in announce_list:
            if isinstance(announce_list_item, list):
                for tracker in announce_list_item:
                    trackers.add(tracker)
            if isinstance(announce_list_item, str):
                trackers.add(announce_list_item)

        return list(trackers)
    
    def __get_trackers_from_magnet(self, magnet: str):
        url_parts = urllib.parse.urlparse(magnet)
        query_parts = urllib.parse.parse_qs(url_parts.query)

        trackers = []
        if "tr" in query_parts:
            trackers = query_parts["tr"]
        
        return trackers
