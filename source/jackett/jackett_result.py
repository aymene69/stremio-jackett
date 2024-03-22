from models.torrent_result import TorrentResult
from utils.detection import detect_language, detect_quality, detect_quality_spec


class JackettResult:
    def __init__(self):
        self.title = None  # Title of the torrent
        self.size = None  # Size of the torrent
        self.link = None  # Download link for the torrent file or magnet url
        self.indexer = None  # Indexer
        self.seeders = None  # Seeders count
        self.magnet = None  # Magnet url
        self.infoHash = None  # infoHash by Jackett
        self.privacy = None  # public or private

    def convert_to_torrent_result(self, media):
        return TorrentResult(
            self.title,
            self.size,
            self.magnet,
            self.infoHash,
            self.link,
            self.seeders,
            detect_language(self.title),
            detect_quality(self.title), 
            detect_quality_spec(self.title),
            self.indexer, episode=media.episode if media.type == "series" else None,
            season=media.season if media.type == "series" else None,
            type=media.type
        )
