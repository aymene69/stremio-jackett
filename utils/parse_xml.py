import xml.etree.ElementTree as ET
import json
import re
import requests
import threading

from utils.get_availability import get_availability
from utils.get_quality import detect_quality, detect_quality_spec

excluded_trackers = ['0day.kiev', '1ptbar', '2 Fast 4 You', '2xFree', '3ChangTrai', '3D Torrents', '3Wmg', '4thD', '52PT', '720pier', 'Abnormal', 'ABtorrents', 'Acid-Lounge', 'Across The Tasman', 'Aftershock', 'AGSVPT', 'Aidoru!Online', 'Aither (API)', 'AlphaRatio', 'Amigos Share Club', 'AniDUB', 'Anime-Free', 'AnimeBytes', 'AnimeLayer', 'AnimeTorrents', 'AnimeTorrents.ro', 'AnimeWorld (API)', 'AniToons', 'Anthelion (API)', 'ArabaFenice', 'ArabP2P', 'ArabTorrents', 'ArenaBG', 'AsianCinema', 'AsianDVDClub', 'Audiences', 'AudioNews', 'Aussierul.es', 'AvistaZ', 'Azusa', 'Back-ups', 'BakaBT', 'BeiTai', 'Beload', 'Best-Core', 'Beyond-HD (API)', 'Bibliotik', 'Bit-Bázis', 'BIT-HDTV', 'Bitded', 'Bithorlo', 'BitHUmen', 'BitPorn', 'Bitspyder', 'Bittorrentfiles', 'BiTTuRK', 'BJ-Share', 'BlueBird', 'Blutopia (API)', 'BookTracker', 'BootyTape', 'Borgzelle', 'Boxing Torrents', 'BrasilTracker', 'BroadcasTheNet', 'BroadCity', 'BrokenStones', 'BrSociety (API)', 'BTArg', 'BTNext', 'BTSCHOOL', 'BwTorrents', 'BYRBT', 'Carp-Hunter', 'Carpathians', 'CarPT', 'CartoonChaos', 'Cathode-Ray.Tube', 'Catorrent', 'Central Torrent', 'CeskeForum', 'CGPeers', 'CHDBits', 'cheggit', 'ChileBT', 'Cinemageddon', 'CinemaMovieS_ZT', 'Cinematik', 'CinemaZ', 'Classix', 'Coastal-Crew', 'Concertos', 'CrazySpirits', 'CrnaBerza', 'CRT2FA', 'Dajiao', 'DanishBytes (API)', 'Dark-Shadow', 'DataScene (API)', 'Deildu', 'Demonoid', 'DesiTorrents (API)', 'Devil-Torrents', 'Diablo Torrent', 'DICMusic', 'DigitalCore', 'DimeADozen', 'DiscFan', 'DivTeam', 'DocsPedia', 'Dream Tracker', 'DreamingTree', 'Drugari', 'DXP', 'Ebooks-Shares', 'Electro-Torrent', 'Empornium', 'Empornium2FA', 'EniaHD', 'Enthralled', 'Enthralled2FA', 'Erai-Raws', 'eShareNet', 'eStone', 'Ex-torrenty', 'exitorrent.org', 'ExKinoRay', 'ExoticaZ', 'ExtremeBits', 'ExtremlymTorrents', 'Falkon Vision Team', 'FANO.IN', 'Fantastiko', 'Fappaizuri', 'FastScene', 'FearNoPeer', 'Femdomcult', 'File-Tracker', 'FileList', 'FinElite', 'FinVip', 'Flux-Zone', 'Free Farm', 'FSM', 'FunFile', 'FunkyTorrents', 'FutureTorrent', 'Fuzer', 'Gamera', 'Gay-Torrents.net', 'gay-torrents.org', 'GAYtorrent.ru', 'GazelleGames', 'GazelleGames (API)', 'Generation-Free (API)', 'Genesis-Movement', 'GigaTorrents', 'GimmePeers', 'Girotorrent', 'GreatPosterWall', 'GreekDiamond', 'HaiDan', 'Haitang', 'HappyFappy', 'Hares Club', 'hawke-uno', 'HD-CLUB', 'HD-CzTorrent', 'HD-Forever', 'HD-Olimpo (API)', 'HD-Only', 'HD-Space', 'HD-Torrents', 'HD-UNiT3D (API)', 'HD4FANS', 'HDArea', 'HDAtmos', 'HDBits (API)', 'HDC', 'HDDolby', 'HDFans', 'HDFun', 'HDGalaKtik', 'HDHome', 'HDMaYi', 'HDPT', 'HDRoute', 'HDSky', 'HDtime', 'HDTorrents.it', 'HDTurk', 'HDU', 'hdvbits', 'HDVIDEO', 'Hebits', 'HellasHut', 'HellTorrents', 'HHanClub', 'HomePornTorrents', 'House of Devil', 'HQMusic', 'HunTorrent', 'iAnon', 'ICC2022', 'Il Corsaro Blu', 'ilDraGoNeRo', 'ImmortalSeed', 'Immortuos', 'Indietorrents', 'Infire', 'Insane Tracker', 'IPTorrents', 'ItaTorrents', 'JME-REUNIT3D (API)', 'JoyHD', 'JPopsuki', 'JPTV (API)', 'KamePT', 'Karagarga', 'Keep Friends', 'KIMOJI', 'Kinorun', 'Kinozal', 'Kinozal (M)', 'Korsar', 'KrazyZone', 'Kufei', 'Kufirc', 'LaidBackManor (API)', 'Last Digital Underground', 'LastFiles', 'Lat-Team (API)', 'Le-Cinephile', 'LearnBits', 'LearnFlakes', 'leech24', 'Les-Cinephiles', 'LeSaloon', 'Lesbians4u', 'Libble', 'LibraNet', 'LinkoManija', 'Locadora', 'LosslessClub', 'LostFilm.tv', 'LST', 'M-Team - TP', 'M-Team - TP (2FA)', 'MaDs Revolution', 'Magnetico (Local DHT)', 'Majomparádé', 'Making Off', 'Marine Tracker', 'Masters-TB', 'Mazepa', 'MDAN', 'MegamixTracker', 'Mendigos da WEB', 'MeseVilág', 'Metal Tracker', 'MetalGuru', 'Milkie', 'MIRCrew', 'MMA-torrents', 'MNV', 'MOJBLiNK', 'MonikaDesign (API)', 'MoreThanTV (API)', 'MouseBits', 'Movie-Torrentz', 'MovieWorld', 'MuseBootlegs', 'MVGroup Forum', 'MVGroup Main', 'MyAnonamouse', 'MySpleen', 'nCore', 'NebulanceAPI', 'NetHD', 'NewStudioL', 'NicePT', 'NoNaMe ClubL', 'NorBits', 'NORDiCHD', 'Ntelogo (API)', 'OKPT', 'Old Toons World', 'OnlyEncodes (API)', 'OpenCD', 'Orpheus', 'OshenPT', 'Ostwiki', 'OurBits', 'P2PBG', 'Panda', 'Party-Tracker', 'PassThePopcorn', 'Peeratiko', 'Peers.FM', 'PigNetwork', 'PixelCove', 'PixelCove2FA', 'PiXELHD', 'PolishSource', 'PolishTracker (API)', 'Pornbay', 'PornoLab', 'Portugas (API)', 'PotUK', 'PreToMe', 'PrivateHD', 'ProAudioTorrents', 'PTCafe', 'PTChina', 'PTerClub', 'PTFiles', 'PThome', 'PTLSP', 'PTSBAO', 'PTTime', 'PT分享站', "Punk's Horror Tracker", 'PuntoTorrent', 'PussyTorrents', 'PuTao', 'PWTorrents', 'R3V WTF!', 'Racing4Everyone (API)', 'RacingForMe', 'Rainbow Tracker', 'RareShare2 (API)', 'Red Leaves', 'Red Star Torrent', 'Redacted', 'RedBits (API)', 'ReelFLiX (API)', 'Resurrect The Net', 'RetroFlix', 'RevolutionTT', 'RGFootball', 'RinTor', 'RiperAM', 'RM-HD', 'RockBox', 'Romanian Metal Torrents', 'Rousi', 'RPTScene', 'RUDUB', 'Rustorka', 'RuTracker', 'SATClubbing', 'SceneHD', 'SceneLinks', 'SceneRush', 'SceneTime', 'Secret Cinema', 'SeedFile', 'seleZen', 'Shadowflow', 'Shareisland (API)', 'Sharewood', 'Sharewood API', 'SharkPT', 'Shazbat', 'SiamBIT', 'SkipTheCommercials (API)', 'SkipTheTrailers', 'SkTorrent', 'SkTorrent-org', 'slosoul', 'SnowPT', 'SoulVoice', 'Speed.cd', 'SpeedApp', 'Speedmaster HD', 'SpeedTorrent Reloaded', 'Spirit of Revolution', 'SportsCult', 'SpringSunday', 'SugoiMusic', 'Superbits', 'Swarmazon (API)', 'Tapochek', 'Tasmanit', 'Team CT Game', 'TeamHD', 'TeamOS', 'TEKNO3D', 'teracod', 'The Crazy Ones', 'The Empire', 'The Falling Angels', 'The Geeks', 'The New Retro', 'The Occult', 'The Old School (API)', 'The Place', 'The Shinning (API)', 'The Show', 'The Vault', 'The-New-Fun', 'TheLeachZone', 'themixingbowl', 'TheRebels (API)', 'TheScenePlace', "Thor's Land", 'TJUPT', 'TLFBits', 'TmGHuB', 'Toca Share', 'Toloka.to', 'ToonsForMe', 'Tornado', 'Torrent Heaven', 'Torrent Network', 'Torrent Sector Crew', 'Torrent Trader', 'Torrent-Explosiv', 'Torrent-Syndikat', 'TOrrent-tuRK', 'Torrent.LT', 'TorrentBD', 'TorrentBytes', 'TorrentCCF', 'TorrentDay', 'TorrentDD', 'Torrenteros (API)', 'TorrentHeaven', 'TorrentHR', 'Torrenting', 'Torrentland', 'Torrentland (API)', 'TorrentLeech', 'Torrentleech.pl', 'TorrentMasters', 'Torrents-Local', 'TorrentSeeds (API)', 'TotallyKids', 'ToTheGlory', 'ToTheGloryCookie', 'TrackerMK', 'TranceTraffic', 'Trellas', 'TreZzoR', 'TreZzoRCookie', 'TribalMixes', 'TurkTorrent', 'TV Store', 'TVChaosUK', 'TvRoad', 'Twisted-Music', 'U2', 'UBits', 'UHDBits', 'UltraHD', 'Union Fansub', 'UnionGang', 'UniOtaku', 'Universal-Torrents', 'Unlimitz', 'upload.cx', 'UTOPIA', 'WDT', 'White Angel', 'WinterSakura', 'World-In-HD', 'World-of-Tomorrow', 'Wukong', 'x-ite.me', 'XbytesV2', 'Xider-Torrent', 'XSpeeds', 'Xthor (API)', 'xTorrenty', 'Xtreme Bytes', 'XWT-Classics', 'XWtorrents', 'YDYPT', 'YGGcookie', 'YGGtorrent', 'Zamunda.net', 'Zelka.org', 'ZmPT (织梦)', 'ZOMB', 'ZonaQ', 'Ztracker']


def cache_torrents(torrents, type, config):
    results = []
    for torrent in torrents:
        if torrent['indexer'] in excluded_trackers:
            continue
        else:
            try:
                torrent_info = get_availability(torrent, config=config)
                if torrent_info is not None:
                    torrent_info['language'] = torrent['language']
                    torrent_info['quality'] = torrent['quality']
                    torrent_info['qualitySpec'] = torrent['qualitySpec']
                    torrent_info['seeders'] = torrent['seeders']
                    torrent_info['size'] = torrent['size']
                    if type == "movie":
                        torrent_info['year'] = torrent['year']
                    if type == "series":
                        torrent_info['season'] = torrent['season']
                        torrent_info['episode'] = torrent['episode']
                        torrent_info['seasonfile'] = torrent['seasonfile']
                    results.append(torrent_info)
            except:
                pass
        try:
            if type == "movie":
                response = requests.post("https://stremio-jackett-cacher.elfhosted.com/pushResult/movie", data=json.dumps(results, indent=4))
                print(response.text)
            if type == "series":
                response = requests.post("https://stremio-jackett-cacher.elfhosted.com/pushResult/series", data=json.dumps(results, indent=4))
                print(response.text)
        except:
            pass


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


def parse_xml(xml_content, query, config):
    if config is None:
        return None
    if config['service'] is None:
        return None
    root = ET.fromstring(xml_content)
    items_list = []
    for item in root.findall('.//item'):

        title = item.find('title').text
        name = item.find('jackettindexer').text + " - " + detect_quality(title) + " " + detect_quality_spec(title)
        size = item.find('size').text
        link = item.find('link').text
        indexer = item.find('jackettindexer').text
        seeders = item.find('.//torznab:attr[@name="seeders"]',
                            namespaces={'torznab': 'http://torznab.com/schemas/2015/feed'}).attrib['value']
        if seeders == "0":
            continue
        item_dict = {}
        if query['type'] == "movie":
            item_dict = {
                "title": title,
                "name": name,
                "size": size,
                "link": link,
                "seeders": seeders,
                "language": detect_language(title),
                "quality": detect_quality(title),
                "qualitySpec": detect_quality_spec(title),
                "year": query['year'],
                "indexer": indexer,
                "type": "movie",
            }
            items_list.append(item_dict)

        if query['type'] == "series":
            if config['language'] == "ru":
                if "S" + str(int(query['season'].replace("S",""))) + "E" + str(int(query['episode'].replace("E", ""))) not in title:
                    if re.search(r'\bS\d+\b', title) is None:
                        continue
            if query['season'] + query['episode'] not in title:
                if re.search(rf'\b{re.escape(query["season"])}\b', title) is None:
                    continue

            item_dict = {
                "title": title,
                "name": name,
                "size": size,
                "link": link,
                "seeders": seeders,
                "language": detect_language(title),
                "quality": detect_quality(title),
                "qualitySpec": detect_quality_spec(title),
                "season": query['season'],
                "episode": query['episode'],
                "indexer": indexer,
                "type": "series",
                "seasonfile": query['seasonfile']
            }
            items_list.append(item_dict)
    sorted_items = sorted(items_list, key=lambda x: int(x['seeders']), reverse=True)
    data = json.dumps(sorted_items, indent=4)
    threading.Thread(target=cache_torrents, args=(sorted_items, query['type'], config)).start()
    return data
