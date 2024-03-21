import requests
import xml.etree.ElementTree as ET

from utils.logger import setup_logger
from models.movie import Movie
from models.series import Series
from jackett.jackett_result import JackettResult

class Jackett:
    def __init__(self, config):
        self.logger = setup_logger(__name__)
        
        self.__api_key = config['jackettApiKey']
        self.__base_url = f"{config['jackettHost']}/api/v2.0"

    def search(self, media):
        self.logger.info("Started Jackett search for " + media.type + " " + media.title)

        if isinstance(media, Movie):
            return self.__search_movie(media)
        elif isinstance(media, Series):
            return self.__search_series(media)
        
        raise TypeError("Only Movie and Series is allowed as media!")
    
    def __search_movie(self, movie):
        url = f"{self.__base_url}/indexers/all/results/torznab/api?apikey={self.__api_key}&t=movie&cat=2000&q={movie.title}&year={movie.year}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            return self.__parse_xml(response.text)
        except Exception:
            self.logger.exception("An exception occured while searching for a movie on Jackett.")
            return []
        
    def __search_series(self, series):
        season = str(int(series.season.replace('S','')))
        episode = str(int(series.episode.replace('E','')))

        url_ep = f"{self.__base_url}/api/v2.0/indexers/all/results/torznab/api?apikey={self.__api_key}&t=tvsearch&cat=5000&q={series.title}&season={season}&ep={episode}"
        url_season = f"{self.__base_url}/api/v2.0/indexers/all/results/torznab/api?apikey={self.__api_key}&t=tvsearch&cat=5000&q={series.title}&season={season}"
        url_title = f"{self.__base_url}/api/v2.0/indexers/all/results/torznab/api?apikey={self.__api_key}&t=tvsearch&cat=5000&q={series.title}"
        
        try:
            # Current functionality is that it returns if the season, episode search was successful. This is subject to change
            response_ep = requests.get(url_ep)
            response_ep.raise_for_status()
            data_ep = self.__parse_xml(response_ep.text)
            if data_ep:
                return data_ep
            
            response_season = requests.get(url_season)
            response_season.raise_for_status()
            data_season = self.__parse_xml(response_season.text)
            if data_season:
                return data_season

            response_title = requests.get(url_title)
            response_title.raise_for_status()
            data_title = self.__parse_xml(response_title.text)
            return data_title
        except Exception:
            self.logger.exception("An exception occured while searching for a series on Jackett.")
            return []
    
    def __parse_xml(self, xml_content):
        xml_root = ET.fromstring(xml_content)
        
        result_list = []
        for item in xml_root.findall('.//item'):
            result = JackettResult()
            
            result.seeders = item.find('.//torznab:attr[@name="seeders"]',namespaces={'torznab': 'http://torznab.com/schemas/2015/feed'}).attrib['value']
            if int(result.seeders) <= 0:
                continue

            result.title = item.find('title').text
            result.size = item.find('size').text
            result.link = item.find('link').text
            result.indexer = item.find('jackettindexer').text
            result.privacy = item.find('type').text
            
            magneturl = item.find('.//torznab:attr[@name="magneturl"]',namespaces={'torznab': 'http://torznab.com/schemas/2015/feed'})
            result.magneturl = magneturl.attrib['value'] if magneturl is not None else None
            
            infoHash = item.find('.//torznab:attr[@name="infohash"]',namespaces={'torznab': 'http://torznab.com/schemas/2015/feed'})
            result.infoHash = infoHash.attrib['value'] if infoHash is not None else None

            result_list.append(result)
        
        return result_list
