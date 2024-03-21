from models.torrent_result import TorrentResult
from utils.get_quality import detect_quality, detect_quality_spec
from utils.parse_xml import detect_language


class JackettResult:
    def __init__(self):
        self.title = None  # Title of the torrent
        self.size = None  # Size of the torrent
        self.link = None  # Download link for the torrent file or magnet url
        self.indexer = None  # Indexer
        self.seeders = None  # Seeders count
        self.magnet_url = None  # Magnet url
        self.infoHash = None  # infoHash by Jackett
        self.privacy = None  # public or private

    def convert_to_torrent_result(self):
        return TorrentResult(self.title, self.size, self.magnet_url, self.infoHash, self.link, self.seeders,
                             detect_language(self.title), detect_quality(self.title), detect_quality_spec(self.title),
                             self.indexer)
