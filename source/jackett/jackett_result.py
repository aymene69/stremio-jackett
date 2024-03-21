class JackettResult:
    def __init__(self):
        self.title = None # Title of the torrent
        self.size = None # Size of the torrent
        self.link = None # Download link for the torrent file or magnet url
        self.indexer = None # Indexer
        self.seeders = None # Seeders count
        self.magneturl = None # Magnet url
        self.infoHash = None # infoHash by Jackett
        self.privacy = None # public or private