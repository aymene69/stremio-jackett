import json
import queue
import threading
from typing import List

from torrent.torrent_item import TorrentItem
from utils.logger import setup_logger
from utils.string_encoding import encodeb64

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


def parse_to_debrid_stream(torrent_item: TorrentItem, configb64, config, results: queue.Queue):

    title = f"{torrent_item.title}\n"

    if torrent_item.file_name is not None:
        title += f"{torrent_item.file_name}\n"

    size_in_gb = round(int(torrent_item.size) / 1024 / 1024 / 1024, 2)


    title += f"👥 {torrent_item.seeders}   💾 {size_in_gb}GB   🔍 {torrent_item.indexer}\n"

    for language in torrent_item.languages:
        title += f"{get_emoji(language)}/"
    title = title[:-1]

    if config['debrid']:
        if torrent_item.availability == True:
            name = f"{INSTANTLY_AVAILABLE}\n"
        else:
            name = f"{DOWNLOAD_REQUIRED}\n"
        name += f"{torrent_item.quality}\n"
        if len(torrent_item.quality_spec) > 0 and torrent_item.quality_spec[0] != "Unknown" and \
                torrent_item.quality_spec[0] != "":
            name += f"({'|'.join(torrent_item.quality_spec)})"

        queryb64 = encodeb64(json.dumps(torrent_item.to_debrid_stream_query())).replace('=', '%3D')

        results.put({
            "name": name,
            "description": title,
            "url": f"{config['addonHost']}/playback/{configb64}/{queryb64}",
            "behaviorHints":{
                "bingeGroup": f"stremio-jackett-{torrent_item.info_hash}",
                "filename": torrent_item.file_name if torrent_item.file_name is not None else torrent_item.title
            }
        })

    if config['torrenting'] and torrent_item.privacy != "private":
        name = f"{DIRECT_TORRENT}\n{torrent_item.quality}\n"
        if len(torrent_item.quality_spec) > 0 and torrent_item.quality_spec[0] != "Unknown" and \
                torrent_item.quality_spec[0] != "":
            name += f"({'|'.join(torrent_item.quality_spec)})"
        results.put({
            "name": name,
            "description": title,
            "infoHash": torrent_item.info_hash,
            "fileIdx": int(torrent_item.file_index) if torrent_item.file_index else None,
            "behaviorHints":{
                "bingeGroup": f"stremio-jackett-{torrent_item.info_hash}",
                "filename": torrent_item.file_name if torrent_item.file_name is not None else torrent_item.title
            }
            # "sources": ["tracker:" + tracker for tracker in torrent_item.trackers]
        })


def parse_to_stremio_streams(torrent_items: List[TorrentItem], config):
    stream_list = []
    threads = []
    thread_results_queue = queue.Queue()

    configb64 = encodeb64(json.dumps(config).replace('=', '%3D'))
    for torrent_item in torrent_items[:int(config['maxResults'])]:
        thread = threading.Thread(target=parse_to_debrid_stream,
                                  args=(torrent_item, configb64, config,
                                        thread_results_queue),
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
