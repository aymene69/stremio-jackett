import json
import queue
import threading
from typing import List

from models.media import Media
from torrent.torrent_item import TorrentItem
from utils.logger import setup_logger
from utils.string_encoding import encodeb64, decodeb64

logger = setup_logger(__name__)

INSTANTLY_AVAILABLE = "[⚡]"
DOWNLOAD_REQUIRED = "[⬇️]"
DIRECT_TORRENT = "[🏴‍☠️]"


# TODO: Languages
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
        "hu": "🇭🇺",
        "la": "🇲🇽",
        "multi": "🌍"
    }
    return emoji_dict.get(language, "🇬🇧")


def filter_by_availability(item):
    if item["name"].startswith(INSTANTLY_AVAILABLE):
        return 0
    else:
        return 1


def filter_by_direct_torrnet(item):
    if item["name"].startswith(DIRECT_TORRENT):
        return 1
    else:
        return 0


def parse_to_debrid_stream(torrent_item: TorrentItem, config, host, results: queue.Queue, media: Media):
    if torrent_item.availability == True:
        name = f"{INSTANTLY_AVAILABLE}\n"
    else:
        name = f"{DOWNLOAD_REQUIRED}\n"

    parsed_data = torrent_item.parsed_data.data

    name += f"{parsed_data.resolution or 'Unknown'}" + (f" ({parsed_data.quality})" if parsed_data.quality else "")

    size_in_gb = round(int(torrent_item.size) / 1024 / 1024 / 1024, 2)

    title = f"{torrent_item.raw_title}\n"

    if torrent_item.file_name is not None:
        title += f"{torrent_item.file_name}\n"

    title += f"👥 {torrent_item.seeders}   💾 {size_in_gb}GB   🔍 {torrent_item.indexer}\n"
    if parsed_data.codec:
        title += f"🎥 {parsed_data.codec.upper()}   "
    if parsed_data.audio:
        title += f"🎧 {', '.join(parsed_data.audio)}"
    if parsed_data.codec or parsed_data.audio:
        title += "\n"

    for language in torrent_item.languages:
        title += f"{get_emoji(language)}/"
    title = title[:-1]

    configb64 = encodeb64(json.dumps(config).replace('=', '%3D'))

    if config['debrid']:
        queryb64 = encodeb64(json.dumps(torrent_item.to_debrid_stream_query(media))).replace('=', '%3D')

        results.put({
            "name": name,
            "description": title,
            "url": f"{host}/playback/{configb64}/{queryb64}",
            "behaviorHints":{
                "bingeGroup": f"stremio-jackett-{torrent_item.info_hash}",
                "filename": torrent_item.file_name if torrent_item.file_name is not None else torrent_item.raw_title # TODO: Use parsed title?
            }
        })

    if config['torrenting'] and (torrent_item.privacy == "public" or torrent_item.indexer == "Cache"):
        name = f"{DIRECT_TORRENT}\n"
        if parsed_data.quality and parsed_data.quality != "Unknown" and \
                parsed_data.quality != "":
            name += f"({parsed_data.quality})"
        results.put({
            "name": name,
            "description": title,
            "infoHash": torrent_item.info_hash,
            "fileIdx": int(torrent_item.file_index) if torrent_item.file_index else None,
            "behaviorHints":{
                "bingeGroup": f"stremio-jackett-{torrent_item.info_hash}",
                "filename": torrent_item.file_name if torrent_item.file_name is not None else torrent_item.raw_title # TODO: Use parsed title?
            }
            # "sources": ["tracker:" + tracker for tracker in torrent_item.trackers]
        })


def parse_to_stremio_streams(torrent_items: List[TorrentItem], config, media):
    stream_list = []
    threads = []
    thread_results_queue = queue.Queue()

    for torrent_item in torrent_items[:int(config['maxResults'])]:
        thread = threading.Thread(target=parse_to_debrid_stream,
                                  args=(torrent_item, config, config['addonHost'],
                                        thread_results_queue, media),
                                  daemon=True)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    while not thread_results_queue.empty():
        stream_list.append(thread_results_queue.get())

    if len(stream_list) == 0:
        return []

    if config['debrid']:
        stream_list = sorted(stream_list, key=filter_by_availability)
        stream_list = sorted(stream_list, key=filter_by_direct_torrnet)
    return stream_list
