class Media:
    def __init__(self, id, title, language, type):
        self.id = id
        self.title = title
        self.language = language
        self.size = None
        self.magnet = None
        self.link = None
        self.seeders = None
        self.quality = None
        self.qualitySpec = None
        self.indexer = None
        self.type = type