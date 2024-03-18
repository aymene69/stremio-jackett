from models.media import Media


class Series(Media):
    def __init__(self, id, title, season, episode, language):
        super().__init__(id, title, language, "series")
        self.season = season
        self.episode = episode
        self.seasonfile = None
