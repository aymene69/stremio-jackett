import concurrent.futures
import base64
import json
from utils.get_availability import get_availability_cached
from utils.get_quality import detect_quality, detect_quality_spec


def get_emoji(language):
    emoji_dict = {
        "fr": "🇫🇷",
        "en": "🇬🇧",
        "es": "🇪🇸",
        "de": "🇩🇪",
        "it": "🇮🇹",
        "pt": "🇵🇹",
        "ru": "🇷🇺",
        "in": "🇮🇳",
        "multi": "🌍"
    }
    return emoji_dict.get(language, "🇬🇧")


def process_stream(stream, cached, stream_type, season, episode, config):
    try:
        if "availability" not in stream and not cached:
            return None
    except:
        return None

    if cached:
        if season is None and episode is None:
            availability = get_availability_cached(stream, stream_type, config=config)
        else:
            availability = get_availability_cached(stream, stream_type, season + episode, config=config)
    else:
        availability = stream.get('availability', False)

    query = {"magnet": stream['magnet'], "type": stream_type}
    if stream_type == "series":
        query['season'] = season
        query['episode'] = episode

    if availability:
        indexer = stream.get('indexer', 'Cached')
        name = f"+{indexer} ({detect_quality(stream['title'])} - {detect_quality_spec(stream['title'])})"
    else:
        indexer = stream.get('indexer', 'Cached')
        name = f"-{indexer} ({detect_quality(stream['title'])} - {detect_quality_spec(stream['title'])})"

    return {
        "name": name,
        "title": f"{stream['title']}\r\n{get_emoji(stream['language'])}   👥 {stream['seeders']}   📂 "
                 f"{round(int(stream['size']) / 1024 / 1024 / 1024, 2)}GB",
        "url": f"{config['addonHost']}/{base64.b64encode(json.dumps(config).encode('utf-8')).decode('utf-8')}/playback/"
               f"{base64.b64encode(json.dumps(query).encode('utf-8')).decode('utf-8')}/{stream['title'].replace(' ', '.')}"
    }


def process_results(items, cached, stream_type, season=None, episode=None, config=None):
    stream_list = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(process_stream, items, [cached] * len(items), [stream_type] * len(items),
                               [season] * len(items), [episode] * len(items), [config] * len(items))

        for result in results:
            if result is not None:
                stream_list.append(result)

    return stream_list
