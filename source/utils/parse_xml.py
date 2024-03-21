import json
import re
import threading
import xml.etree.ElementTree as ET

from utils.cache import cache_results
from utils.get_quality import detect_quality, detect_and_format_quality_spec
from utils.logger import setup_logger

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


def detect_language(torrent_name):
    language_patterns = {
        "fr": r'\b(FRENCH|FR|VF|VF2|VFF|TRUEFRENCH|VFQ|FRA)\b',
        "en": r'\b(ENGLISH|EN|ENG)\b',
        "es": r'\b(SPANISH|ES|ESP)\b',
        "de": r'\b(GERMAN|DE|GER)\b',
        "it": r'\b(ITALIAN|IT|ITA)\b',
        "pt": r'\b(PORTUGUESE|PT|POR)\b',
        "ru": r'\b(RUSSIAN|RU|RUS)\b',
        "in": r'\b(INDIAN|IN|HINDI|TELUGU|TAMIL|KANNADA|MALAYALAM|PUNJABI|MARATHI|BENGALI|GUJARATI|URDU|ODIA|ASSAMESE|KONKANI|MANIPURI|NEPALI|SANSKRIT|SINHALA|SINDHI|TIBETAN|BHOJPURI|DHIVEHI|KASHMIRI|KURUKH|MAITHILI|NEWARI|RAJASTHANI|SANTALI|SINDHI|TULU)\b',
        "nl": r'\b(DUTCH|NL|NLD)\b',
    }

    for language, pattern in language_patterns.items():
        if re.search(pattern, torrent_name, re.IGNORECASE):
            return language

    if re.search(r'\bMULTI\b', torrent_name, re.IGNORECASE):
        return "multi"

    return "en"


def parse_xml(xml_content, media, config):
    if config is None:
        return None
    if config['service'] is None:
        return None
    root = ET.fromstring(xml_content)
    items_list = []
    for item in root.findall('.//item'):

        title = item.find('title').text
        name = item.find('jackettindexer').text + " - " + detect_quality(title) + " " + detect_and_format_quality_spec(
            title)
        size = item.find('size').text
        link = item.find('link').text
        indexer = item.find('jackettindexer').text
        seeders = item.find('.//torznab:attr[@name="seeders"]',
                            namespaces={'torznab': 'http://torznab.com/schemas/2015/feed'}).attrib['value']
        if seeders == "0":
            continue
        item_dict = {}
        if media.type == "movie":
            item_dict = {
                "title": title,
                "name": name,
                "size": size,
                "link": link,
                "seeders": seeders,
                "language": detect_language(title),
                "quality": detect_quality(title),
                "qualitySpec": detect_and_format_quality_spec(title),
                "year": media.year,
                "indexer": indexer,
                "type": "movie",
            }
            items_list.append(item_dict)

        if media.type == "series":
            if config['language'] == "ru":
                if "S" + str(int(media.season.replace("S", ""))) + "E" + str(
                        int(media.episode.replace("E", ""))) not in title:
                    if re.search(r'\bS\d+\b', title) is None:
                        continue
            if media.season + media.episode not in title:
                if re.search(rf'\b{re.escape(media.season)}\b', title) is None:
                    continue

            item_dict = {
                "title": title,
                "name": name,
                "size": size,
                "link": link,
                "seeders": seeders,
                "language": detect_language(title),
                "quality": detect_quality(title),
                "qualitySpec": detect_and_format_quality_spec(title),
                "season": media.season,
                "episode": media.episode,
                "indexer": indexer,
                "type": "series",
                "seasonfile": media.seasonfile
            }
            items_list.append(item_dict)
    sorted_items = sorted(items_list, key=lambda x: int(x['seeders']), reverse=True)
    data = json.dumps(sorted_items, indent=4)
    threading.Thread(target=cache_results, daemon=True, args=(sorted_items, media.type, config)).start()
    return data
