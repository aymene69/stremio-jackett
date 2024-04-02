import re


def detect_quality(torrent_name):
    quality_patterns = {
        "4k": r'\b(2160P|UHD|4K)\b',
        "1080p": r'\b(1080P|FHD|FULLHD|HD|HIGHDEFINITION)\b',
        "720p": r'\b(720P|HD|HIGHDEFINITION)\b',
        "480p": r'\b(480P|SD|STANDARDDEFINITION)\b'
    }

    for quality, pattern in quality_patterns.items():
        if re.search(pattern, torrent_name, re.IGNORECASE):
            return quality
    return "Unknown"


def detect_and_format_quality_spec(torrent_name):
    qualities = detect_quality_spec(torrent_name)
    return "/".join(qualities) if qualities else "Unknown"


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


def detect_languages(torrent_name):
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
        "hu": r'\b(HUNGARIAN|HU|HUN)\b',
        "la": r'\b(LATIN|LATINO|LA)\b',
        "multi": r"\b(MULTI)\b"
    }

    languages = []
    for language, pattern in language_patterns.items():
        if re.search(pattern, torrent_name, re.IGNORECASE):
            languages.append(language)

    if re.search(r'\bMULTI\b', torrent_name, re.IGNORECASE):
        languages.append("multi")

    if len(languages) == 0:
        return ["en"]

    return languages
