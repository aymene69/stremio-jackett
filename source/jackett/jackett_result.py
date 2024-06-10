from RTN import parse

from models.series import Series
from torrent.torrent_item import TorrentItem
from utils.logger import setup_logger

logger = setup_logger(__name__)

class JackettResult:
    def __init__(self):
        self.raw_title = None  # Raw title of the torrent
        self.size = None  # Size of the torrent
        self.link = None  # Download link for the torrent file or magnet url
        self.indexer = None  # Indexer
        self.seeders = None  # Seeders count
        self.magnet = None  # Magnet url
        self.info_hash = None  # infoHash by Jackett
        self.privacy = None  # public or private

        # Extra processed details for further filtering
        self.languages = None  # Language of the torrent
        self.type = None  # series or movie

        self.parsed_data = None  # Ranked result

    def convert_to_torrent_item(self):
        return TorrentItem(
            self.raw_title,
            self.size,
            self.magnet,
            self.info_hash.lower() if self.info_hash is not None else None,
            self.link,
            self.seeders,
            self.languages,
            self.indexer,
            self.privacy,
            self.type,
            self.parsed_data
        )

    def from_cached_item(self, cached_item, media):
        if type(cached_item) is not dict:
            logger.error(cached_item)

        parsed_result = parse(cached_item['title'])

        self.raw_title = cached_item['title']
        self.indexer = "Cache"  # Cache doesn't return an indexer sadly (It stores it tho)
        self.magnet = cached_item['magnet']
        self.link = cached_item['magnet']
        self.info_hash = cached_item['hash']
        self.languages = cached_item['language'].split(";") if cached_item['language'] is not None else []
        self.seeders = cached_item['seeders']
        self.size = cached_item['size']
        self.type = media.type
        self.parsed_data = parsed_result

        return self
