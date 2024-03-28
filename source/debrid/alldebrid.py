# alldebrid.py
import json

from constants import NO_CACHE_VIDEO_URL
from debrid.base_debrid import BaseDebrid
from utils.logger import setup_logger

logger = setup_logger(__name__)


class AllDebrid(BaseDebrid):
    def __init__(self, config):
        super().__init__(config)
        self.base_url = "https://api.alldebrid.com/v4/"

    def add_magnet(self, magnet):
        url = f"{self.base_url}magnet/upload?agent=jackett&apikey={self.config['debridKey']}&magnet={magnet}"
        return self.get_json_response(url)

    def check_magnet_status(self, id):
        url = f"{self.base_url}magnet/status?agent=jackett&apikey={self.config['debridKey']}&id={id}"
        return self.get_json_response(url)

    def unrestrict_link(self, link):
        url = f"{self.base_url}link/unlock?agent=jackett&apikey={self.config['debridKey']}&link={link}"
        return self.get_json_response(url)

    def get_stream_link(self, query):
        query_details = json.loads(query)
        magnet = query_details['magnet']
        stream_type = query_details['type']
        data = self.add_magnet(magnet)
        if not data:
            return "Error: Failed to upload magnet."

        magnet_id = data["data"]['magnets'][0]['id']

        if not self.wait_for_ready_status(
                lambda: self.check_magnet_status(magnet_id)["data"]["magnets"]["status"] == "Ready"):
            return NO_CACHE_VIDEO_URL

        # Logic to select the appropriate link based on type
        if stream_type == "movie":
            link = max(data["data"]["magnets"]['links'], key=lambda x: x['size'])['link']
        elif stream_type == "series":
            season_episode = query_details['season'] + query_details['episode']
            link = next(
                (link["link"] for link in data["data"]["magnets"]["links"] if season_episode in link["filename"]), None)
        else:
            return "Error: Unsupported stream type."

        unlocked_link_data = self.unrestrict_link(link)
        if not unlocked_link_data:
            return "Error: Failed to unlock link."

        return unlocked_link_data["data"]["link"]

    def get_availability_bulk(self, hashes_or_magnets):
        if len(hashes_or_magnets) == 0:
            logger.info("No hashes to be sent to Real-Debrid.")
            return dict()

        url = f"{self.base_url}magnet/instant?agent=jackett&apikey={self.config['debridKey']}&magnets[]={'&magnets[]='.join(hashes_or_magnets)}"
        return self.get_json_response(url)
