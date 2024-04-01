import re

from utils.filter.language_filter import LanguageFilter
from utils.filter.max_size_filter import MaxSizeFilter
from utils.filter.quality_exclusion_filter import QualityExclusionFilter
from utils.filter.results_per_quality_filter import ResultsPerQualityFilter
from utils.filter.title_exclusion_filter import TitleExclusionFilter
from utils.logger import setup_logger

logger = setup_logger(__name__)

quality_order = {"4k": 0, "1080p": 1, "720p": 2, "480p": 3}


def sort_quality(item):
    return quality_order.get(item.quality, float('inf')), item.quality is None


def items_sort(items, config):
    if config['sort'] == "quality":
        return sorted(items, key=sort_quality)
    if config['sort'] == "sizeasc":
        return sorted(items, key=lambda x: int(x.size))
    if config['sort'] == "sizedesc":
        return sorted(items, key=lambda x: int(x.size), reverse=True)
    if config['sort'] == "qualitythensize":
        return sorted(items, key=lambda x: (sort_quality(x), -int(x.size)))
    return items


# def filter_season_episode(items, season, episode, config):
#     filtered_items = []
#     for item in items:
#         if config['language'] == "ru":
#             if "S" + str(int(season.replace("S", ""))) + "E" + str(
#                     int(episode.replace("E", ""))) not in item['title']:
#                 if re.search(rf'\bS{re.escape(str(int(season.replace("S", ""))))}\b', item['title']) is None:
#                     continue
#         if re.search(rf'\b{season}\s?{episode}\b', item['title']) is None:
#             if re.search(rf'\b{season}\b', item['title']) is None:
#                 continue

#         filtered_items.append(item)
#     return filtered_items

def filter_out_non_matching(items, season, episode):
    filtered_items = []
    for item in items:
        title = item.title.upper()
        season_pattern = r'S\d+'
        episode_pattern = r'E\d+'

        season_substrings = re.findall(season_pattern, title)
        if len(season_substrings) > 0 and season not in season_substrings:
            continue

        episode_substrings = re.findall(episode_pattern, title)
        if len(episode_substrings) > 0 and episode not in episode_substrings:
            continue

        filtered_items.append(item)

    return filtered_items


def filter_items(items, media, config):
    filters = {
        "languages": LanguageFilter(config),
        "maxSize": MaxSizeFilter(config, media.type),  # Max size filtering only happens for movies, so it
        "exclusionKeywords": TitleExclusionFilter(config),
        "exclusion": QualityExclusionFilter(config),
        "resultsPerQuality": ResultsPerQualityFilter(config)
    }

    # Filtering out 100% non matching for series
    logger.info(f"Item count before filtering: {len(items)}")
    if media.type == "series":
        logger.info(f"Filtering out non matching series torrents")
        items = filter_out_non_matching(items, media.season, media.episode)
        logger.info(f"Item count changed to {len(items)}")

    for filter_name, filter_instance in filters.items():
        try:
            logger.info(f"Filtering by {filter_name}: " + str(config[filter_name]))
            items = filter_instance(items)
            logger.info(f"Item count changed to {len(items)}")
        except Exception as e:
            logger.error(f"Error while filtering by {filter_name}", exc_info=e)
    logger.info(f"Item count after filtering: {len(items)}")
    logger.info("Finished filtering torrents")

    return items


def sort_items(items, config):
    if config['sort'] is not None:
        return items_sort(items, config)
    else:
        return items
