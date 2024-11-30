import requests

from metdata.metadata_provider_base import MetadataProvider
from models.media import Media
from models.movie import Movie
from models.series import Series
from utils.logger import setup_logger

class TMDB(MetadataProvider):
    def __init__(self, config):
        super().__init__(config)
        self._indexers = None
        
    @property
    def indexers(self):
        return self._indexers
    @indexers.setter
    def indexers(self, indexers_):
        self._indexers = indexers_
    
    def get_metadata(self, id, type):
        self.logger.info("Getting metadata for " + type + " with id " + id)

        full_id = id.split(":")

        result = None
        if self.config['getAllLanguages'] and self._indexers and len(self._indexers) > 0:
          languages = list({indexer.language for indexer in self._indexers}) # Use set to remove duplicated languages
        else:
          languages = self.config['languages']
        for lang in languages:
            url = f"https://api.themoviedb.org/3/find/{full_id[0]}?api_key={self.config['tmdbApi']}&external_source=imdb_id&language={lang}"
            response = requests.get(url)
            data = response.json()

            if lang == languages[0]:
                if type == "movie":
                    result = Movie(
                        id=id,
                        titles=[self.replace_weird_characters(data["movie_results"][0]["title"])],
                        year=data["movie_results"][0]["release_date"][:4],
                        languages=languages
                    )
                else:
                    result = Series(
                        id=id,
                        titles=[self.replace_weird_characters(data["tv_results"][0]["name"])],
                        season="S{:02d}".format(int(full_id[1])),
                        episode="E{:02d}".format(int(full_id[2])),
                        languages=languages
                    )
            else:
                if type == "movie":
                    result.titles.append(self.replace_weird_characters(data["movie_results"][0]["title"]))
                else:
                    result.titles.append(self.replace_weird_characters(data["tv_results"][0]["name"]))

        self.logger.info("Got metadata for " + type + " with id " + id)
        return result
