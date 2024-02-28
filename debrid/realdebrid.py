import json

from debrid.base_debrid import BaseDebrid


class RealDebrid(BaseDebrid):
    def __init__(self, config):
        super().__init__(config)
        self.base_url = "https://api.real-debrid.com"

    def add_magnet(self, magnet):
        url = f"{self.base_url}/rest/1.0/torrents/addMagnet"
        headers = {"Authorization": f"Bearer {self.config['debridKey']}"}
        data = {"magnet": magnet}
        return self.get_json_response(url, method='post', headers=headers, data=data)

    def get_torrent_info(self, torrent_id):
        url = f"{self.base_url}/rest/1.0/torrents/info/{torrent_id}"
        headers = {"Authorization": f"Bearer {self.config['debridKey']}"}
        return self.get_json_response(url, headers=headers)

    def select_files(self, torrent_id, files):
        url = f"{self.base_url}/rest/1.0/torrents/selectFiles/{torrent_id}"
        headers = {"Authorization": f"Bearer {self.config['debridKey']}"}
        data = {"files": files}
        return self.get_json_response(url, method='post', headers=headers, data=data)

    def unrestrict_link(self, link):
        url = f"{self.base_url}/rest/1.0/unrestrict/link"
        headers = {"Authorization": f"Bearer {self.config['debridKey']}"}
        data = {"link": link}
        return self.get_json_response(url, method='post', headers=headers, data=data)

    def get_stream_link(self, query):
        query_details = json.loads(query)
        magnet = query_details['magnet']
        stream_type = query_details['type']

        magnet_response = self.add_magnet(magnet)
        if not magnet_response or 'id' not in magnet_response:
            return "Error: Failed to add magnet."

        torrent_id = magnet_response['id']
        torrent_info = self.get_torrent_info(torrent_id)
        if not torrent_info or 'files' not in torrent_info:
            return "Error: Failed to get torrent info."

        # Selecting files based on stream type, this is a simplified example
        if stream_type == "movie":
            # Assuming we select the largest file for movies
            largest_file_id = max(torrent_info['files'], key=lambda x: x['bytes'])['id']
            select_response = self.select_files(torrent_id, str(largest_file_id))
            if not select_response:
                return "Error: Failed to select files."
        elif stream_type == "series":
            # Implement logic to select the correct episode file
            # This is placeholder logic and needs to be replaced with actual episode selection
            season_episode = f"{query_details.get('season')}{query_details.get('episode')}"
            file_id = next((file['id'] for file in torrent_info['files'] if season_episode in file['path']), None)
            if not file_id:
                return "Error: Episode file not found."
            select_response = self.select_files(torrent_id, str(file_id))
            if not select_response:
                return "Error: Failed to select files."
        else:
            return "Error: Unsupported stream type."

        # Assuming direct download link is available after file selection
        # This might require additional steps based on Real-Debrid's API
        download_link = torrent_info.get('links', [None])[0]
        if not download_link:
            return "Error: Download link not found."

        # Unrestricting the download link
        unrestrict_response = self.unrestrict_link(download_link)
        if not unrestrict_response or 'download' not in unrestrict_response:
            return "Error: Failed to unrestrict link."

        return unrestrict_response['download']
