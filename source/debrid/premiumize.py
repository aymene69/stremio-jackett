# Assuming the BaseDebrid class and necessary imports are already defined as shown previously
import json

from constants import NO_CACHE_VIDEO_URL
from debrid.base_debrid import BaseDebrid
from utils.general import get_info_hash_from_magnet, season_episode_in_filename
from utils.logger import setup_logger

logger = setup_logger(__name__)

class Premiumize(BaseDebrid):
    def __init__(self, config):
        super().__init__(config)
        self.base_url = "https://www.premiumize.me/api"

    def add_magnet(self, magnet):
        url = f"{self.base_url}/transfer/create?apikey={self.config['debridKey']}"
        form = {'src': magnet}
        return self.get_json_response(url, method='post', data=form)
    
    #Doesn't work for the time being. Premiumize does not support torrent file torrents
    def add_torrent(self, torrent_file):
        url = f"{self.base_url}/transfer/create?apikey={self.config['debridKey']}"
        form = {'file': torrent_file}
        return self.get_json_response(url, method='post', data=form)
    
    def list_transfers(self):
        url = f"{self.base_url}/transfer/list?apikey={self.config['debridKey']}"
        return self.get_json_response(url)

    def get_folder_or_file_details(self, item_id, is_folder=True):
        if is_folder:
            url = f"{self.base_url}/folder/list?id={item_id}&apikey={self.config['debridKey']}"
        else:
            url = f"{self.base_url}/item/details?id={item_id}&apikey={self.config['debridKey']}"
        return self.get_json_response(url)
    
    def get_availability(self, hash):
        url = f"{self.base_url}/cache/check?apikey={self.config['debridKey']}&items[]={hash}"
        return self.get_json_response(url)
    
    def get_availability_bulk(self, hashes_or_magnets):
        url = (f"{self.base_url}/cache/check?apikey={self.config['debridKey']}&items[]=") + "&items[]=".join(hashes_or_magnets)
        return self.get_json_response(url)

    def get_stream_link(self, query):
        query = json.loads(query)
        magnet = query['magnet']
        info_hash = get_info_hash_from_magnet(magnet)
        stream_type = query['type']
        #torrent_download = unquote(query["torrent_download"]) if query["torrent_download"] is not None else None
        
        transfer_data = self.add_magnet(magnet)
        if not transfer_data or 'id' not in transfer_data:
            return "Error: Failed to create transfer."
        transfer_id = transfer_data['id']
        if not self.wait_for_ready_status(lambda: self.get_availability(info_hash)["transcoded"][0] == True):
            return NO_CACHE_VIDEO_URL

        # Assuming the transfer is complete, we need to find whether it's a file or a folder
        transfers = self.list_transfers()
        item_id, is_folder = None, False
        for item in transfers.get('transfers', []):
            if item['id'] == transfer_id:
                if item.get('folder_id'):
                    item_id = item['folder_id']
                    is_folder = True
                else:
                    item_id = item['file_id']
                break

        if not item_id:
            return "Error: Transfer completed but no item ID found."

        details = self.get_folder_or_file_details(item_id, is_folder)

        if stream_type == "movie":
            # For movies, we pick the largest file in the folder or the file itself
            if is_folder:
                link = max(details.get("content", []), key=lambda x: x["size"])["link"]
            else:
                link = details.get('link')
                
        elif stream_type == "series":
            if is_folder:
                season = query["season"]
                episode = query["episode"]
                files = details.get("content", [])
                strict_matching_files = []
                matching_files = []
                
                for file in files:
                    if season_episode_in_filename(file["name"], season, episode, strict=True):
                        strict_matching_files.append(file)
                    elif season_episode_in_filename(file["name"], season, episode, strict=False):
                        matching_files.append(file)

                if len(strict_matching_files) > 0:
                    matching_files = strict_matching_files
                    
                if len(matching_files) == 0:
                    return "Error: No matching files for {season} {episode} in torrent."
                
                link = max(matching_files, key=lambda x: x["size"])["link"]
            else:
                link = details.get('link')
        else:
            return "Error: Unsupported stream type."

        return link
