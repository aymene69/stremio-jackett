import concurrent.futures
import json

from utils.detection import detect_quality, detect_and_format_quality_spec
from utils.logger import setup_logger
from utils.string_encoding import encodeb64

logger = setup_logger(__name__)

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
        "nl": "🇳🇱",
        "multi": "🌍"
    }
    return emoji_dict.get(language, "🇬🇧")


def filter_by_availability(item):
    availability = item["name"][0]
    return 0 if availability == "+" else 1


def process_stream(stream, cached, stream_type, season, episode, debrid_service, config):
    if cached:
        if season is None and episode is None:
            availability = debrid_service.get_availability(stream.magnet, stream_type)
        else:
            availability = debrid_service.get_availability(stream.magnet, stream_type, season + episode)
    else:
        availability = stream.availability

    query = {"magnet": stream.magnet, "type": stream_type}
    if stream_type == "series":
        query['season'] = season
        query['episode'] = episode
    if availability == "AUTH_BLOCKED":
        return {"name": "AUTH_BLOCKED",
                "title": "New connection on AllDebrid.\r\nPlease authorize the connection\r\non your email",
                "url": "#"
                }
    if availability:
        indexer = stream.indexer
        name = f"+{indexer} ({detect_quality(stream.title)} - {detect_and_format_quality_spec(stream.title)})"
    else:
        indexer = stream.indexer
        name = f"-{indexer} ({detect_quality(stream.title)} - {detect_and_format_quality_spec(stream.title)})"
    configb64 = encodeb64(json.dumps(config)).replace('=', '%3D')
    queryb64 = encodeb64(json.dumps(query)).replace('=', '%3D')
    return {
        "name": name,
        "title": f"{stream.title}\r\n{get_emoji(stream.language)}   👥 {stream.seeders}   📂 "
                 f"{round(int(stream.size) / 1024 / 1024 / 1024, 2)}GB",
        "url": f"{config['addonHost']}/playback/{configb64}/{queryb64}/{stream.title.replace(' ', '.')}"
    }


def process_results(items, cached, stream_type, season=None, episode=None, debrid_service=None, config=None):
    stream_list = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(process_stream, items, [cached] * len(items), [stream_type] * len(items),
                               [season] * len(items), [episode] * len(items), [debrid_service] * len(items),
                               [config] * len(items))

        for result in results:
            if result is not None:
                stream_list.append(result)

    return sorted(stream_list, key=filter_by_availability)
