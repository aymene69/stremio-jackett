import re

from utils.logger import setup_logger

logger = setup_logger(__name__)


def detect_quality_spec(torrent_name):
    quality_patterns = {
        "HDR": r'\b(HDR|HDR10|HDR10PLUS|HDR10PLUS|HDR10PLUS)\b',
        "DTS": r'\b(DTS|DTS-HD)\b',
        "DDP": r'\b(DDP|DDP5.1|DDP7.1)\b',
        "DD": r'\b(DD|DD5.1|DD7.1)\b',
        "SDR": r'\b(SDR|SDRIP)\b',
        "WEBDL": r'\b(WEBDL|WEB-DL|WEB)\b',
        "BLURAY": r'\b(BLURAY|BLU-RAY|BD)\b',
        "DVDRIP": r'\b(DVDRIP|DVDR)\b',
        "CAM": r'\b(CAM|CAMRIP|CAM-RIP)\b',
        "TS": r'\b(TS|TELESYNC|TELESYNC)\b',
        "TC": r'\b(TC|TELECINE|TELECINE)\b',
        "R5": r'\b(R5|R5LINE|R5-LINE)\b',
        "DVDSCR": r'\b(DVDSCR|DVD-SCR)\b',
        "HDTV": r'\b(HDTV|HDTVRIP|HDTV-RIP)\b',
        "PDTV": r'\b(PDTV|PDTVRIP|PDTV-RIP)\b',
        "DSR": r'\b(DSR|DSRRIP|DSR-RIP)\b',
        "WORKPRINT": r'\b(WORKPRINT|WP)\b',
        "VHSRIP": r'\b(VHSRIP|VHS-RIP)\b',
        "VODRIP": r'\b(VODRIP|VOD-RIP)\b',
        "TVRIP": r'\b(TVRIP|TV-RIP)\b',
        "WEBRIP": r'\b(WEBRIP|WEB-RIP)\b',
        "BRRIP": r'\b(BRRIP|BR-RIP)\b',
        "BDRIP": r'\b(BDRIP|BD-RIP)\b',
        "HDCAM": r'\b(HDCAM|HD-CAM)\b',
        "HDRIP": r'\b(HDRIP|HD-RIP)\b',
    }
    qualities = []
    for quality, pattern in quality_patterns.items():
        if re.search(pattern, torrent_name, re.IGNORECASE):
            qualities.append(quality)
    return qualities if qualities else None


def filter_language(torrents, language):
    logger.info(f"Filtering torrents by language: {language}")
    filtered_torrents = []
    for torrent in torrents:
        if type(torrent) is str:
            logger.error(f"Torrent is a string: {torrent}")
            continue
        if not torrent['language']:
            continue
        if torrent['language'] == language:
            filtered_torrents.append(torrent)
        if torrent['language'] == "multi":
            filtered_torrents.append(torrent)
        if torrent['language'] == "no":
            filtered_torrents.append(torrent)
    return filtered_torrents


def max_size(items, config):
    logger.info("Started filtering size")
    if config is None:
        return items
    if config['maxSize'] is None:
        return items
    filtered_items = []
    size = int(config['maxSize']) * 1024 ** 3
    for item in items:
        if int(item['size']) <= size:
            filtered_items.append(item)
    return filtered_items


def quality_exclusion(streams, config):
    logger.info("Started filtering quality")
    RIPS = ["HDRIP", "BRRIP", "BDRIP", "HDCAM", "WEBRIP", "TVRIP", "VODRIP", "HDRIP"]
    CAMS = ["CAM", "TS", "TC", "R5", "DVDSCR", "HDTV", "PDTV", "DSR", "WORKPRINT", "VHSRIP"]

    if config is None or config['exclusion'] is None:
        return streams

    filtered_items = []
    excluded_qualities = config['exclusion']
    rips = "rips" in excluded_qualities
    cams = "cams" in excluded_qualities

    for stream in streams:
        if stream['quality'] not in excluded_qualities:
            detection = detect_quality_spec(stream['title'])
            if detection is not None:
                for item in detection:
                    if rips and item in RIPS:
                        break
                    if cams and item in CAMS:
                        break
                else:
                    filtered_items.append(stream)
        else:
            filtered_items.append(stream)

    return filtered_items


def results_per_quality(items, config):
    logger.info("Started filtering results per quality (" + str(config['resultsPerQuality']) + " results per quality)")
    if config is None:
        return items
    if config['resultsPerQuality'] is None or int(config['resultsPerQuality']) == 0:
        return items
    filtered_items = []
    quality_count = {}
    for item in items:
        if item['quality'] not in quality_count:
            quality_count[item['quality']] = 1
            filtered_items.append(item)
        else:
            if quality_count[item['quality']] < int(config['resultsPerQuality']):
                quality_count[item['quality']] += 1
                filtered_items.append(item)

    logger.info("Item count changed from " + str(len(items)) + " to " + str(len(filtered_items)))
    return filtered_items


def sort_quality(item):
    order = {"4k": 0, "1080p": 1, "720p": 2, "480p": 3}
    return order.get(item.get("quality"), float('inf')), item.get("quality") is None


def items_sort(items, config):
    if config is None:
        return items
    if config['sort'] is None:
        return items
    if config['sort'] == "quality":
        return sorted(items, key=sort_quality)
    if config['sort'] == "sizeasc":
        return sorted(items, key=lambda x: int(x['size']))
    if config['sort'] == "sizedesc":
        return sorted(items, key=lambda x: int(x['size']), reverse=True)


def filter_season_episode(items, season, episode, config):
    filtered_items = []
    for item in items:
        if config['language'] == "ru":
            if "S" + str(int(season.replace("S", ""))) + "E" + str(
                    int(episode.replace("E", ""))) not in item['title']:
                if re.search(rf'\bS{re.escape(str(int(season.replace("S", ""))))}\b', item['title']) is None:
                    continue
        if season + episode not in item['title']:
            if re.search(rf'\b{season}\b', item['title']) is None:
                continue
    return filtered_items


def filter_items(items, item_type=None, config=None, cached=False, season=None, episode=None):
    if config is None:
        return items
    if config['language'] is None:
        return items
    if cached and item_type == "series":
        items = filter_season_episode(items, season, episode, config)
    logger.info("Started filtering torrents")
    items = filter_language(items, config['language'])
    if int(config['maxSize']) != 0:
        if item_type == "movie":
            items = max_size(items, config)
    if config['sort'] is not None:
        items = items_sort(items, config)
    if config['exclusion'] is not None:
        items = quality_exclusion(items, config)
    if config['resultsPerQuality'] is not None:
        items = results_per_quality(items, config)
    return items
