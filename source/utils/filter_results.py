import re

from utils.filter.language_filter import LanguageFilter
from utils.filter.max_size_filter import MaxSizeFilter
from utils.filter.quality_exclusion_filter import QualityExclusionFilter
from utils.filter.results_per_quality_filter import ResultsPerQualityFilter
from utils.filter.title_exclusion_filter import TitleExclusionFilter
from utils.logger import setup_logger

logger = setup_logger(__name__)


def sort_quality(item):
    order = {"4k": 0, "1080p": 1, "720p": 2, "480p": 3}
    return order.get(item.get("quality"), float('inf')), item.get("quality") is None


def items_sort(items, config):
    if config['sort'] == "quality":
        return sorted(items, key=sort_quality)
    if config['sort'] == "sizeasc":
        return sorted(items, key=lambda x: int(x['size']))
    if config['sort'] == "sizedesc":
        return sorted(items, key=lambda x: int(x['size']), reverse=True)
    return items


def filter_season_episode(items, season, episode, config):
    filtered_items = []
    for item in items:
        if config['language'] == "ru":
            if "S" + str(int(season.replace("S", ""))) + "E" + str(
                    int(episode.replace("E", ""))) not in item['title']:
                if re.search(rf'\bS{re.escape(str(int(season.replace("S", ""))))}\b', item['title']) is None:
                    continue
        if re.search(rf'\b{season}\s?{episode}\b', item['title']) is None:
            if re.search(rf'\b{season}\b', item['title']) is None:
                continue

        filtered_items.append(item)
    return filtered_items


def filter_items(items, item_type=None, config=None, cached=False, season=None, episode=None):
    if config is None:
        return items

    filters = {
        "language": LanguageFilter(config),
        "maxSize": MaxSizeFilter(config, item_type),
        "exclusionKeywords": TitleExclusionFilter(config),
        "exclusion": QualityExclusionFilter(config),
        "resultsPerQuality": ResultsPerQualityFilter(config)
    }

    if cached and item_type == "series":
        items = filter_season_episode(items, season, episode, config)
    logger.info("Started filtering torrents")

    logger.info(f"Item count before filtering: {len(items)}")
    for filter_name, filter_instance in filters.items():
        try:
            logger.info(f"Filtering by {filter_name}: " + str(config[filter_name]))
            items = filter_instance(items)
            logger.info(f"Item count changed to {len(items)}")
        except Exception as e:
            logger.error(f"Error while filtering by {filter_name}", exc_info=e)
    logger.info("Finished filtering torrents")

    if config['sort'] is not None:
        items = items_sort(items, config)
    return items

def series_file_filter(files, season, episode):
    if season == None or episode == None:
        return []

    season = season.lower()
    episode = episode.lower()

    filtered_files = []

    # Main filter
    for file in files:
        if season + episode in file['path'].lower():
            filtered_files.append(file)


    if len(filtered_files) != 0:
        return filtered_files

    # Secondary fallback filter
    for file in files:
        filepath = file['path'].lower()
        if season in filepath and episode in filepath:
            filtered_files.append(file)

    if len(filtered_files) != 0:
        return filtered_files

    # Third fallback filter
    season = season[1:]
    episode = episode[1:]
    for file in files:
        filepath = file['path'].lower()
        if season in filepath and episode in filepath and filepath.index(season) > filepath.index(episode):
            filtered_files.append(file) 

    if len(filtered_files) != 0:
        return filtered_files

    # Last fallback filter
    if season[0] == '0': season = season[1:]
    if episode[0] == '0': episode = episode[1:]

    for file in files:
        filepath = file['path'].lower()
        if season in filepath and episode in filepath and filepath.index(season) > filepath.index(episode):
            filtered_files.append(file) 

    return filtered_files