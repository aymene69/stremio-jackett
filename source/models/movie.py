from models.media import Media


class Movie(Media):
    def __init__(self, id, title, year, language):
        super().__init__(id, title, language, "movie")
        self.year = year
