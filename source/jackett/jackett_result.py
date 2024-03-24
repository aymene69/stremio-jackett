from torrent.torrent_item import TorrentItem
from utils.detection import detect_language, detect_quality, detect_quality_spec


class JackettResult:
    def __init__(self):
        self.title = None  # Title of the torrent
        self.size = None  # Size of the torrent
        self.link = None  # Download link for the torrent file or magnet url
        self.indexer = None  # Indexer
        self.seeders = None  # Seeders count
        self.magnet = None  # Magnet url
        self.info_hash = None  # infoHash by Jackett
        self.privacy = None  # public or private

        # Extra processed details for further filtering
        self.language = None # Language of the torrent
        self.quality = None # Quality of the torrent
        self.quality_spec = None # Quality specifications of the torrent
        self.type = None # series or movie

        # Not sure about these
        self.season = None # Season, if the media is a series
        self.episode = None # Episode, if the media is a series

    def convert_to_torrent_item(self):
        return TorrentItem(
            self.title,
            self.size,
            self.magnet,
            self.info_hash.lower() if self.info_hash is not None else None,
            self.link,
            self.seeders,
            self.language,
            self.quality, 
            self.quality_spec,
            self.indexer,
            self.episode,
            self.season,
            self.type
        )
