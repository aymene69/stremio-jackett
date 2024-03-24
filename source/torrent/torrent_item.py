class TorrentItem:
    def __init__(self, title, size, magnet, info_hash, link, seeders, language, quality, quality_spec, indexer,
                 episode=None, season=None, type=None):
        self.title = title  # Title of the torrent - it may be updated durring __process_torrent()
        self.size = size  # Size of the video file inside of the torrent - it may be updated durring __process_torrent()
        self.magnet = magnet  # Magnet to torrent
        self.info_hash = info_hash  # Hash of the torrent
        self.link = link  # Link to download torrent file or magnet link
        self.seeders = seeders  # The number of seeders
        self.language = language  # Language of the torrent
        self.quality = quality  # Quality of the torrent
        self.quality_spec = quality_spec  # Quality specifications of the torrent
        self.indexer = indexer  # Indexer of the torrent
        self.episode = episode  # Episode if its a series (for example: "E01" or "E14")
        self.season = season  # Season if its a series (for example: "S01" or "S14")
        self.type = type  # "series" or "movie"

        self.files = None  # The files inside of the torrent. If it's None, it means that there is only one file inside of the torrent
        self.torrent = None  # The torrent binary, if its None, it means that there is only a magnet link provided by Jackett. It also means, that we cant do series file filtering before debrid.
        self.trackers = []  # Trackers of the torrent
        self.file_index = None  # Index of the file inside of the torrent - it may be updated durring __process_torrent() and update_availability(). If the index is None and torrent is not None, it means that the series episode is not inside of the torrent.

        self.availability = False  # If its instantly available on the debrid service
