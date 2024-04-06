import os
import queue
import threading
import time
import xml.etree.ElementTree as ET

import requests

from jackett.jackett_indexer import JackettIndexer
from jackett.jackett_result import JackettResult
from models.movie import Movie
from models.series import Series
from utils import detection
from utils.logger import setup_logger


class JackettService:
    def __init__(self, config):
        self.logger = setup_logger(__name__)

        self.__api_key = config['jackettApiKey']
        self.__base_url = f"{config['jackettHost']}/api/v2.0"
        self.__session = requests.Session()

    def search(self, media):
        self.logger.info("Started Jackett search for " + media.type + " " + media.titles[0])

        indexers = self.__get_indexers()
        threads = []
        results_queue = queue.Queue()  # Create a Queue instance to hold the results

        # Define a wrapper function that calls the actual target function and stores its return value in the queue
        def thread_target(media, indexer):
            self.logger.info(f"Searching on {indexer.title}")
            start_time = time.time()

            # Call the actual function
            if isinstance(media, Movie):
                result = self.__search_movie_indexer(media, indexer)
            elif isinstance(media, Series):
                result = self.__search_series_indexer(media, indexer)
            else:
                raise TypeError("Only Movie and Series is allowed as media!")

            self.logger.info(
                f"Search on {indexer.title} took {time.time() - start_time} seconds and found {len(result)} results")

            results_queue.put(result)  # Put the result in the queue

        for indexer in indexers:
            # Pass the wrapper function as the target to Thread, with necessary arguments
            threads.append(threading.Thread(target=thread_target, args=(media, indexer)))

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        results = []

        # Retrieve results from the queue and append them to the results list
        while not results_queue.empty():
            results.extend(results_queue.get())

        flatten_results = [result for sublist in results for result in sublist]

        return self.__post_process_results(flatten_results, media)

    def __search_movie_indexer(self, movie, indexer):

        # url = f"{self.__base_url}/indexers/all/results/torznab/api?apikey={self.__api_key}&t=movie&cat=2000&q={movie.title}&year={movie.year}"

        has_imdb_search_capability = (os.getenv(
            "DISABLE_JACKETT_IMDB_SEARCH") != "true" and indexer.movie_search_capatabilities is not None and 'imdbid' in indexer.movie_search_capatabilities)

        if has_imdb_search_capability:
            languages = ['en']
            index_of_language = [index for index, lang in enumerate(movie.languages) if lang == 'en'][0]
            titles = [movie.titles[index_of_language]]
        elif indexer.language == "en":
            languages = movie.languages
            titles = movie.titles
        else:
            index_of_language = [index for index, lang in enumerate(movie.languages) if lang == indexer.language or lang == 'en']
            languages = [movie.languages[index] for index in index_of_language]
            titles = [movie.titles[index] for index in index_of_language]

        results = []

        for index, lang in enumerate(languages):
            params = {
                'apikey': self.__api_key,
                't': 'movie',
                'cat': '2000',
                'q': titles[index],
                'year': movie.year,
            }

            if has_imdb_search_capability:
                params['imdbid'] = movie.id

            url = f"{self.__base_url}/indexers/{indexer.id}/results/torznab/api"
            url += '?' + '&'.join([f'{k}={v}' for k, v in params.items()])

            try:
                response = self.__session.get(url)
                response.raise_for_status()
                results.append(self.__get_torrent_links_from_xml(response.text))
            except Exception:
                self.logger.exception(
                    f"An exception occured while searching for a movie on Jackett with indexer {indexer.title} and "
                    f"language {lang}.")

        return results

    def __search_series_indexer(self, series, indexer):
        season = str(int(series.season.replace('S', '')))
        episode = str(int(series.episode.replace('E', '')))


        has_imdb_search_capability = (os.getenv("DISABLE_JACKETT_IMDB_SEARCH") != "true"
                                      and indexer.tv_search_capatabilities is not None
                                      and 'imdbid' in indexer.tv_search_capatabilities)
        if has_imdb_search_capability:
            languages = ['en']
            index_of_language = [index for index, lang in enumerate(series.languages) if lang == 'en'][0]
            titles = [series.titles[index_of_language]]
        elif indexer.language == "en":
            languages = series.languages
            titles = series.titles
        else:
            index_of_language = [index for index, lang in enumerate(series.languages) if
                                 lang == indexer.language or lang == 'en']
            languages = [series.languages[index] for index in index_of_language]
            titles = [series.titles[index] for index in index_of_language]

        results = []

        for index, lang in enumerate(languages):
            params = {
                'apikey': self.__api_key,
                't': 'tvsearch',
                'cat': '5000',
                'q': titles[index],
            }

            if has_imdb_search_capability:
                params['imdbid'] = series.id

            url_title = f"{self.__base_url}/indexers/{indexer.id}/results/torznab/api"
            url_title += '?' + '&'.join([f'{k}={v}' for k, v in params.items()])

            url_season = f"{self.__base_url}/indexers/{indexer.id}/results/torznab/api"
            params['season'] = season
            url_season += '?' + '&'.join([f'{k}={v}' for k, v in params.items()])

            url_ep = f"{self.__base_url}/indexers/{indexer.id}/results/torznab/api"
            params['ep'] = episode
            url_ep += '?' + '&'.join([f'{k}={v}' for k, v in params.items()])

            try:
                # Current functionality is that it returns if the season, episode search was successful. This is subject to change
                # TODO: what should we prioritize? season, episode or title?
                response_ep = self.__session.get(url_ep)
                response_ep.raise_for_status()

                response_season = self.__session.get(url_season)
                response_season.raise_for_status()

                data_ep = self.__get_torrent_links_from_xml(response_ep.text)
                data_season = self.__get_torrent_links_from_xml(response_season.text)

                if data_ep:
                    results.append(data_ep)
                if data_season:
                    results.append(data_season)

                if not data_ep and not data_season:
                    response_title = self.__session.get(url_title)
                    response_title.raise_for_status()
                    data_title = self.__get_torrent_links_from_xml(response_title.text)
                    if data_title:
                        results.append(data_title)
            except Exception:
                self.logger.exception(
                    f"An exception occured while searching for a series on Jackett with indexer {indexer.title} and language {lang}.")

        return results

    def __get_indexers(self):
        url = f"{self.__base_url}/indexers/all/results/torznab/api?apikey={self.__api_key}&t=indexers&configured=true"

        try:
            response = self.__session.get(url)
            response.raise_for_status()
            return self.__get_indexer_from_xml(response.text)
        except Exception:
            self.logger.exception("An exception occured while getting indexers from Jackett.")
            return []

    def __get_indexer_from_xml(self, xml_content):
        xml_root = ET.fromstring(xml_content)

        indexer_list = []
        for item in xml_root.findall('.//indexer'):
            indexer = JackettIndexer()

            indexer.title = item.find('title').text
            indexer.id = item.attrib['id']
            indexer.link = item.find('link').text
            indexer.type = item.find('type').text
            indexer.language = item.find('language').text.split('-')[0]

            self.logger.info(f"Indexer: {indexer.title} - {indexer.link} - {indexer.type}")

            movie_search = item.find('.//searching/movie-search[@available="yes"]')
            tv_search = item.find('.//searching/tv-search[@available="yes"]')

            if movie_search is not None:
                indexer.movie_search_capatabilities = movie_search.attrib['supportedParams'].split(',')
            else:
                self.logger.info(f"Movie search not available for {indexer.title}")

            if tv_search is not None:
                indexer.tv_search_capatabilities = tv_search.attrib['supportedParams'].split(',')
            else:
                self.logger.info(f"TV search not available for {indexer.title}")

            indexer_list.append(indexer)

        return indexer_list

    def __get_torrent_links_from_xml(self, xml_content):
        xml_root = ET.fromstring(xml_content)

        result_list = []
        for item in xml_root.findall('.//item'):
            result = JackettResult()

            result.seeders = item.find('.//torznab:attr[@name="seeders"]',
                                       namespaces={'torznab': 'http://torznab.com/schemas/2015/feed'}).attrib['value']
            if int(result.seeders) <= 0:
                continue

            result.title = item.find('title').text
            result.size = item.find('size').text
            result.link = item.find('link').text
            result.indexer = item.find('jackettindexer').text
            result.privacy = item.find('type').text

            # TODO: I haven't seen this in the Jackett XML response. Is this still relevant?
            # Or which indexers provide this?
            magnet = item.find('.//torznab:attr[@name="magneturl"]',
                               namespaces={'torznab': 'http://torznab.com/schemas/2015/feed'})
            result.magnet = magnet.attrib['value'] if magnet is not None else None

            infoHash = item.find('.//torznab:attr[@name="infohash"]',
                                 namespaces={'torznab': 'http://torznab.com/schemas/2015/feed'})
            result.info_hash = infoHash.attrib['value'] if infoHash is not None else None

            result_list.append(result)

        return result_list

    def __post_process_results(self, results, media):
        for result in results:
            result.languages = detection.detect_languages(result.title)
            result.quality = detection.detect_quality(result.title)
            result.quality_spec = detection.detect_quality_spec(result.title)
            result.type = media.type

            if isinstance(media, Series):
                result.season = media.season
                result.episode = media.episode

        return results
