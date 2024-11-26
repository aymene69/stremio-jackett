from RTN import title_match, RTN, DefaultRanking, SettingsModel, sort_torrents

from utils.filter.language_filter import LanguageFilter
from utils.filter.max_size_filter import MaxSizeFilter
from utils.filter.quality_exclusion_filter import QualityExclusionFilter
from utils.filter.results_per_quality_filter import ResultsPerQualityFilter
from utils.filter.title_exclusion_filter import TitleExclusionFilter
from utils.logger import setup_logger

logger = setup_logger(__name__)

quality_order = {"4k": 0, "2160p": 0, "1080p": 1, "720p": 2, "480p": 3}


def sort_quality(item):
    if len(item.parsed_data.data.resolution) == 0:
        return float('inf'), True

    # TODO: first resolution?
    return quality_order.get(item.parsed_data.data.resolution[0],
                             float('inf')), item.parsed_data.data.resolution is None


def items_sort(items, config):
    logger.info(config)

    settings = SettingsModel(
        require=[],
        exclude=config['exclusionKeywords'] + config['exclusion'],
        preferred=[],
        # custom_ranks={
        #     "uhd": CustomRank(enable=True, fetch=True, rank=200),
        #     "hdr": CustomRank(enable=True, fetch=True, rank=100),
        # }
    )

    rtn = RTN(settings=settings, ranking_model=DefaultRanking())
    torrents = [rtn.rank(item.raw_title, item.info_hash) for item in items]
    sorted_torrents = sort_torrents(set(torrents))

    for key, value in sorted_torrents.items():
        index = next((i for i, item in enumerate(items) if item.info_hash == key), None)
        if index is not None:
            items[index].parsed_data = value

    logger.info(items)

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

# TODO: not needed anymore because of RTN
def filter_out_non_matching(items, season, episode):
    filtered_items = []
    for item in items:
        logger.info(season)
        logger.info(episode)
        logger.info(item.parsed_data)
        clean_season = season.replace("S", "")
        clean_episode = episode.replace("E", "")
        numeric_season = int(clean_season)
        numeric_episode = int(clean_episode)

        if len(item.parsed_data.season) == 0 and len(item.parsed_data.episode) == 0:
            continue

        if len(item.parsed_data.episode) == 0 and numeric_season in item.parsed_data.season:
            filtered_items.append(item)
            continue

        if numeric_season in item.parsed_data.season and numeric_episode in item.parsed_data.episode:
            filtered_items.append(item)
            continue


    return filtered_items


def remove_non_matching_title(items, titles):
    logger.info(titles)
    filtered_items = []
    for item in items:
        for title in titles:
            if not title_match(title, item.parsed_data.parsed_title):
                continue

            filtered_items.append(item)
            break

    return filtered_items


def filter_items(items, media, config):
    filters = {
        "languages": LanguageFilter(config),
        "maxSize": MaxSizeFilter(config, media.type),  # Max size filtering only happens for movies, so it
        "exclusionKeywords": TitleExclusionFilter(config),
        "exclusion": QualityExclusionFilter(config),
        "resultsPerQuality": ResultsPerQualityFilter(config)
    }

    # Filtering out 100% non-matching for series
    logger.info(f"Item count before filtering: {len(items)}")
    if media.type == "series":
        logger.info(f"Filtering out non matching series torrents")
        items = filter_out_non_matching(items, media.season, media.episode)
        logger.info(f"Item count changed to {len(items)}")

    # TODO: is titles[0] always the correct title? Maybe loop through all titles and get the highest match?
    items = remove_non_matching_title(items, media.titles)

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
