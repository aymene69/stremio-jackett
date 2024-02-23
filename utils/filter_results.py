import re


def filter_language(torrents, language):
    print(f"Filtering torrents by language: {language}")
    filtered_torrents = []
    for torrent in torrents:
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
    print("Started filtering size")
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


def quality_exclusion(items, config):
    print("Started filtering quality")
    if config is None:
        return items
    if config['exclusion'] is None:
        return items
    filtered_items = []
    for item in items:
        if item['quality'] not in config['exclusion']:
            filtered_items.append(item)
    return filtered_items

def results_per_quality(items, config):
    print("Started filtering results per quality (" + str(config['resultsPerQuality']) + " results per quality)")
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

    print("Item count changed from " + str(len(items)) + " to " + str(len(filtered_items)))
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
    print("Started filtering torrents")
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
