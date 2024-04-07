import requests

from metdata.metadata_provider_base import MetadataProvider
from models.movie import Movie
from models.series import Series


class Cinemeta(MetadataProvider):
    def get_metadata(self, id, type):
        self.logger.info("Getting metadata for " + type + " with id " + id)

        full_id = id.split(":")

        url = f"https://v3-cinemeta.strem.io/meta/{type}/{full_id[0]}.json"
        response = requests.get(url)
        data = response.json()

        if type == "movie":
            result = Movie(
                id=id,
                titles=[self.replace_weird_characters(data["meta"]["name"])],
                year=data["meta"]["year"],
                languages=["en"]
            )
        else:
            result = Series(
                id=id,
                titles=[self.replace_weird_characters(data["meta"]["name"])],
                season="S{:02d}".format(int(full_id[1])),
                episode="E{:02d}".format(int(full_id[2])),
                languages=["en"]
            )

        self.logger.info("Got metadata for " + type + " with id " + id)
        return result
