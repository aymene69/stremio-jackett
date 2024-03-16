import requests
import bencode
import hashlib

from utils.get_quality import detect_quality
from utils.get_quality import detect_quality_spec
from utils.process_results import get_emoji

from utils.logger import setup_logger
logger = setup_logger(__name__)

from constants import NO_RESULTS

max_retries = 5


def get_torrent_stream(item):
    season = item['season'] if 'season' in item else None
    episode = item['episode'] if 'episode' in item else None

    # If the link is a magnet on its own
    if item['link'].startswith("magnet:"):
        magnet_link = item['link']
        urn_part = magnet_link.split('xt=urn:')[1]
        hash = urn_part[urn_part.find(':')+1 : urn_part.find('&')]

        # Not yet finished
        stream_info = {
            "name": item['name'],
            "title": item['title'],
            "hash": hash,
            "episodeFileIdx": None,
            "indexer": item['indexer'],
            "language": item['language'],
            "seeders": item['seeders'],
            "size": item['size'],
        }
        return process_torrent_stream(stream_info)
    
    # If the link is a torrent download
    response = requests.get(item['link'])
    logger.info("Getting torrent info")
    attempts = 0
    while response.status_code != 200 and attempts < max_retries:
        logger.info("Retrying")
        response = requests.get(item['link'])
        attempts += 1

    if response.status_code == 200:
        logger.info("Successfully retrieved torrent info")
    else:
        logger.error("Failed to retrieve torrent info after " + str(max_retries) + " attempts")
        return NO_RESULTS
    
    logger.info("Got torrent info")
    torrent = bencode.bdecode(response.content)

    trackers = set()
    if 'announce-list' in torrent:
        for tracker in torrent['announce-list']:
            if len(tracker) > 0:
                trackers.add("tracker:" + tracker[0])
    
    if 'announce' in torrent:
        #Some torrents have lists for these for some reason
        if isinstance(torrent['announce'], list):
            for tracker in torrent['announce']:
                trackers.add("tracker:" + tracker)
        else:
            trackers.add("tracker:" + torrent['announce'])

    episodeFileIdx = None
    if item['type'] == "series":
        try:
            filtered_files = series_file_filter(torrent['info']['files'], season, episode)
            video_file = max(filtered_files, key=lambda x: x['length'])
            episodeFileIdx = video_file['index']
        except:
            return None

    trackers = list(trackers)
    stream_info = {
        "name": item['name'],
        "title": item['title'],
        "hash": hashlib.sha1(bencode.bencode(torrent['info'])).hexdigest(),
        "episodeFileIdx": episodeFileIdx,
        "indexer": item['indexer'],
        "language": item['language'],
        "seeders": item['seeders'],
        "size": item['size'],
        "trackers": list(trackers)
    }

    logger.info("Returning torrent info")
    return process_torrent_stream(stream_info)


def process_torrent_stream(stream):
    name = f"{stream['indexer']} ({detect_quality(stream['title'])} - {detect_quality_spec(stream['title'])})"

    streamData = {
        "name": name,
        "title": f"{stream['title']}\r\n{get_emoji(stream['language'])}   👥 {stream['seeders']}   📂 "
                 f"{round(int(stream['size']) / 1024 / 1024 / 1024, 2)}GB",
        "infoHash": stream['hash'],
        "sources": stream['trackers']
    }

    if stream['episodeFileIdx']:
        streamData['fileIdx'] = stream['episodeFileIdx']

    return streamData

def series_file_filter(files, season, episode):
    if season == None or episode == None:
        return []

    season = season.lower()
    episode = episode.lower()

    filtered_files = []
    
    # Main filter
    index = 0
    for file in files:
        if season + episode in file['path'][0].lower():
            file['index'] = index
            filtered_files.append(file)
        index = index + 1


    if len(filtered_files) != 0:
        return filtered_files
    
    # Secondary fallback filter
    index = 0
    for file in files:
        filepath = file['path'][0].lower()
        if season in filepath and episode in filepath:
            file['index'] = index
            filtered_files.append(file)
        index = index + 1

    if len(filtered_files) != 0:
        return filtered_files
    
    # Third fallback filter
    index = 0
    season = season[1:]
    episode = episode[1:]
    for file in files:
        filepath = file['path'][0].lower()
        if season in filepath and episode in filepath and filepath.index(season) > filepath.index(episode):
            file['index'] = index
            filtered_files.append(file)
        index = index + 1
    
    if len(filtered_files) != 0:
        return filtered_files
    
    # Last fallback filter
    index = 0
    if season[0] == '0': season = season[1:]
    if episode[0] == '0': episode = episode[1:]
    for file in files:
        filepath = file['path'][0].lower()
        if season in filepath and episode in filepath and filepath.index(season) > filepath.index(episode):
            file['index'] = index
            filtered_files.append(file)
        index = index + 1

    return filtered_files