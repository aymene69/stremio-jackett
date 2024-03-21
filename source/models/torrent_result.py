class TorrentResult:
    def __init__(self, title, size, magnet, info_hash, link, seeders, language, quality, quality_spec, indexer):
        self.title = title
        self.size = size
        self.magnet = magnet
        self.info_hash = info_hash
        self.link = link
        self.seeders = seeders
        self.language = language
        self.quality = quality
        self.quality_spec = quality_spec
        self.indexer = indexer
