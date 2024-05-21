from RTN import parse

from models.series import Series
from torrent.torrent_item import TorrentItem


class JackettResult:
    def __init__(self):
        self.title = None  # Parsed title of the torrent
        self.raw_title = None  # Raw title of the torrent
        self.title = None  # Title of the torrent
        self.size = None  # Size of the torrent
        self.link = None  # Download link for the torrent file or magnet url
        self.indexer = None  # Indexer
        self.seeders = None  # Seeders count
        self.magnet = None  # Magnet url
        self.info_hash = None  # infoHash by Jackett
        self.privacy = None  # public or private

        # Extra processed details for further filtering
        self.languages = None  # Language of the torrent
        self.resolution = None  # Resolution of the torrent
        self.quality = None  # Quality of the torrent
        self.type = None  # series or movie
        self.codec = None  # Codec of the media
        self.audio = None  # Audio of the media

        # Not sure about these
        self.season = None  # Season, if the media is a series
        self.episode = None  # Episode, if the media is a series

    def convert_to_torrent_item(self):
        return TorrentItem(
            self.title,
            self.raw_title,
            self.size,
            self.magnet,
            self.info_hash.lower() if self.info_hash is not None else None,
            self.link,
            self.seeders,
            self.languages,
            self.resolution,
            self.quality,
            self.codec,
            self.audio,
            self.indexer,
            self.privacy,
            self.episode,
            self.season,
            self.type
        )

    def from_cached_item(self, cached_item, media):
        parsed_result = parse(cached_item['title'])

        self.title = cached_item['title']
        self.title = parsed_result.parsed_title
        self.indexer = "Cache"  # Cache doesn't return an indexer sadly (It stores it tho)
        self.magnet = cached_item['magnet']
        self.link = cached_item['magnet']
        self.info_hash = cached_item['hash']
        self.languages = cached_item['language'].split(";") if cached_item['language'] is not None else []
        self.resolution = parsed_result.resolution
        self.quality = parsed_result.quality
        self.codec = parsed_result.codec
        self.audio = parsed_result.audio
        self.seeders = cached_item['seeders']
        self.size = cached_item['size']

        if isinstance(media, Series):
            self.season = media.season
            self.episode = media.episode
            self.type = media.type
        else:
            self.type = media.type

        return self
