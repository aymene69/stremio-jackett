from urllib.parse import quote

from utils.logger import setup_logger


class TorrentItem:
    def __init__(self, title, size, magnet, info_hash, link, seeders, languages, quality, quality_spec, indexer,
                 privacy,
                 episode=None, season=None, type=None):
        self.logger = setup_logger(__name__)

        self.title = title  # Title of the torrent
        self.size = size  # Size of the video file inside of the torrent - it may be updated durring __process_torrent()
        self.magnet = magnet  # Magnet to torrent
        self.info_hash = info_hash  # Hash of the torrent
        self.link = link  # Link to download torrent file or magnet link
        self.seeders = seeders  # The number of seeders
        self.languages = languages  # Language of the torrent
        self.quality = quality  # Quality of the torrent
        self.quality_spec = quality_spec if quality_spec is not None else []  # Quality specifications of the torrent
        self.indexer = indexer  # Indexer of the torrent
        self.episode = episode  # Episode if its a series (for example: "E01" or "E14")
        self.season = season  # Season if its a series (for example: "S01" or "S14")
        self.type = type  # "series" or "movie"
        self.privacy = privacy  # "public" or "private"

        self.file_name = None  # it may be updated durring __process_torrent()
        self.files = None  # The files inside of the torrent. If it's None, it means that there is only one file inside of the torrent
        self.torrent_download = None  # The torrent jackett download url if its None, it means that there is only a magnet link provided by Jackett. It also means, that we cant do series file filtering before debrid.
        self.trackers = []  # Trackers of the torrent
        self.file_index = None  # Index of the file inside of the torrent - it may be updated durring __process_torrent() and update_availability(). If the index is None and torrent is not None, it means that the series episode is not inside of the torrent.

        self.availability = False  # If its instantly available on the debrid service

    def to_debrid_stream_query(self) -> dict:
        return {
            "magnet": self.magnet,
            "type": self.type,
            "file_index": self.file_index,
            "season": self.season,
            "episode": self.episode,
            "torrent_download": quote(self.torrent_download) if self.torrent_download is not None else None
        }
