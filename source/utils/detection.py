import re


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

    if len(languages) == 0:
        return ["en"]

    return languages
