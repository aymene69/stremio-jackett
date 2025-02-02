import re
import requests
from time import sleep
from metdata.metadata_provider_base import MetadataProvider
from models.movie import Movie
from models.series import Series

class Cinemeta(MetadataProvider):
    def get_metadata(self, id, type):
        self.logger.info("Getting metadata for " + type + " with id " + id)
        full_id = id.split(":")
        url = f"https://v3-cinemeta.strem.io/meta/{type}/{full_id[0]}.json"
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = requests.get(url)
                data = response.json()
                
                # Check if data or data["meta"] is empty
                if not data or not data.get("meta"):
                    retry_count += 1
                    if retry_count == max_retries:
                        raise ValueError(f"Empty response after {max_retries} retries for {id}")
                    sleep(1)  # Wait 1 second before retrying
                    continue
                
                if type == "movie":

                    year = data["meta"].get("year")
                    if not year:
                        release_info = data["meta"].get("releaseInfo")
                        if re.search(r"\d{4}", release_info):
                            year = re.search(r"\d{4}", release_info).group()

                    result = Movie(
                        id=id,
                        titles=[self.replace_weird_characters(data["meta"]["name"])],
                        year=year,
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
                
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    raise Exception(f"Failed to get metadata after {max_retries} retries: {str(e)}")
                sleep(1)  # Wait 1 second before retrying