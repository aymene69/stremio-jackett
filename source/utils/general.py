from utils.logger import setup_logger

logger = setup_logger(__name__)

video_formats = {".mkv", ".mp4", ".avi", ".mov", ".flv", ".wmv", ".webm", ".mpg", ".mpeg", ".m4v", ".3gp", ".3g2",
                 ".ogv",
                 ".ogg", ".drc", ".gif", ".gifv", ".mng", ".avi", ".mov", ".qt", ".wmv", ".yuv", ".rm", ".rmvb", ".asf",
                 ".amv", ".m4p", ".m4v", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".mpg", ".mpeg", ".m2v", ".m4v",
                 ".svi", ".3gp", ".3g2", ".mxf", ".roq", ".nsv", ".flv", ".f4v", ".f4p", ".f4a", ".f4b"}


def season_episode_in_filename(filename, season, episode, strict=False):
    if not is_video_file(filename):
        return False

    if strict:
        if not season.lower().startswith("s"):
            season = "s" + season
        if not episode.lower().startswith("e"):
            episode = "e" + episode
    else:
        if season.lower().startswith("s"):
            season = season[1:]
        if episode.lower().startswith("e"):
            episode = episode[1:]

    filename = filename.lower()
    season = season.lower()
    episode = episode.lower()

    return season in filename and episode in filename and filename.index(season) < filename.rindex(episode)


def get_info_hash_from_magnet(magnet: str):
    exact_topic_index = magnet.find("xt=")
    if exact_topic_index == -1:
        logger.debug(f"No exact topic in magnet {magnet}")
        return None

    exact_topic_substring = magnet[exact_topic_index:]
    end_of_exact_topic = exact_topic_substring.find("&")
    if end_of_exact_topic != -1:
        exact_topic_substring = exact_topic_substring[:end_of_exact_topic]

    info_hash = exact_topic_substring[exact_topic_substring.rfind(":") + 1:]

    return info_hash.lower()


def is_video_file(filename):
    extension_idx = filename.rfind(".")
    if extension_idx == -1:
        return False

    return filename[extension_idx:] in video_formats
