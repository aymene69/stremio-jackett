from typing import List, Dict
from torrent.torrent_item import TorrentItem
from debrid.alldebrid import AllDebrid
from debrid.realdebrid import RealDebrid
from debrid.premiumize import Premiumize

from utils.logger import setup_logger

class TorrentSmartContainer:
    def __init__(self, torrent_items: List[TorrentItem]):
        self.logger = setup_logger(__name__)
        self.__itemsDict: Dict[TorrentItem] = self.__build_items_dict_by_infohash(torrent_items)
    
    def get_hashes(self):        
        return self.__itemsDict.keys()
    
    def update_availability(self, debrid_response, debrid_type):
        if debrid_type is RealDebrid:
            self.__update_availability_realdebrid(debrid_response)
        elif debrid_type is AllDebrid:
            self.__update_availability_alldebrid(debrid_response)
        elif debrid_type is Premiumize:
            self.__update_availability_premiumize(debrid_response)
        else:
            raise NotImplemented

    def __update_availability_realdebrid(self, response):
        for info_hash, details in response.items():
            if "rd" not in details:
                continue
        
            torrent_item: TorrentItem = self.__itemsDict[info_hash]

            if torrent_item.type == "series":
                season = torrent_item.season.replace("S","")
                episode = torrent_item.episode.replace("E","")
                
                for variants in details["rd"]:
                    if torrent_item.availability == True:
                        break
                    
                    for file_index, file in variants.items():
                        if self.__series_season_episode_available(file["filename"], season, episode):
                            torrent_item.availability = True
                            torrent_item.file_index = file_index
                            break
            else:
                torrent_item.availability = True

    def __update_availability_alldebrid(self, response):
        if response["status"] != "success":
            return
        
        for data in response["data"]["magnets"]:
            if data["instant"] == False:
                continue
            
            torrent_item: TorrentItem = self.__itemsDict[data["hash"]]
            if torrent_item.type == "series":
                season = torrent_item.season.replace("S","")
                episode = torrent_item.episode.replace("E","")

                if torrent_item.availability == True:
                    break

                file_index = 1
                for file in data["files"]:
                    if self.__series_season_episode_available(file["n"], season, episode):
                        torrent_item.availability = True
                        torrent_item.file_index = file_index
                        break
                    file_index += 1

    def __update_availability_premiumize(self, response):
        #I don't understand the premiumize api
        pass

    def __build_items_dict_by_infohash(self, items: List[TorrentItem]):
        items_dict = dict()
        for item in items:
            if item.info_hash is not None:
                items_dict[item.info_hash] = item
        return items_dict

    def __series_season_episode_available(self, filename, season, episode):   
        return season in filename and episode in filename and filename.index(season) < filename.index(episode)
