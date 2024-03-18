# Assuming the BaseDebrid class and necessary imports are already defined as shown previously
import json

from constants import NO_CACHE_VIDEO_URL
from debrid.base_debrid import BaseDebrid


class Premiumize(BaseDebrid):
    def __init__(self, config):
        super().__init__(config)
        self.base_url = "https://www.premiumize.me/api"

    def add_magnet(self, magnet):
        url = f"{self.base_url}/transfer/create?apikey={self.config['debridKey']}"
        form = {'src': magnet}
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

    def get_stream_link(self, query):
        query_details = json.loads(query)
        magnet = query_details['magnet']
        stream_type = query_details['type']

        transfer_data = self.add_magnet(magnet)
        if not transfer_data or 'id' not in transfer_data:
            return "Error: Failed to create transfer."

        transfer_id = transfer_data['id']

        if not self.wait_for_ready_status(lambda: any(
                item['id'] == transfer_id and item['status'] == "finished" for item in
                self.list_transfers().get('transfers', []))):
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
            # For series, more specific logic to pick the correct episode would be needed
            season_episode = query_details.get('season') + query_details.get('episode')
            if is_folder:
                link = next(
                    (content["link"] for content in details.get("content", []) if season_episode in content["name"]),
                    None)
            else:
                link = details.get('link')
        else:
            return "Error: Unsupported stream type."

        return link
