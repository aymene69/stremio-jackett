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
        "multi": "🌍"
    }
    return emoji_dict.get(language, "🇬🇧")


def process_results(items, cached, stream_type, season=None, episode=None, config=None):
    stream_list = []
    for stream in items:
        try:
            if "availability" not in stream and cached == False:
                continue
        except:
            continue
        if cached:
            if season == None and episode == None:
                availability = get_availability_cached(stream, stream_type, config=config)
            else:
                availability = get_availability_cached(stream, stream_type, season+episode, config=config)
        else:
            availability = stream['availability']

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

        stream_list.append({
            "name": name,
            "title": f"{stream['title']}\r\n{get_emoji(stream['language'])}👥{stream['seeders']}📂"
                     f"{round(int(stream['size']) / 1024 / 1024 / 1024, 2)}GB",
            "url": f"{config['addonHost']}/{base64.b64encode(json.dumps(config).encode('utf-8')).decode('utf-8')}/playback/"
                   f"{base64.b64encode(json.dumps(query).encode('utf-8')).decode('utf-8')}/{stream['title']}"
        })

    return stream_list
