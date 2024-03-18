from utils.filter.base_filter import BaseFilter
from utils.logger import setup_logger

logger = setup_logger(__name__)


class LanguageFilter(BaseFilter):
    def __init__(self, config):
        super().__init__(config)

    def filter(self, data):
        filtered_data = []
        for torrent in data:
            if type(torrent) is str:
                logger.error(f"Torrent is a string: {torrent}")
                continue
            if not torrent['language']:
                continue
            if torrent['language'] == self.config['language']:
                filtered_data.append(torrent)
            if torrent['language'] == "multi":
                filtered_data.append(torrent)
            if torrent['language'] == "no":
                filtered_data.append(torrent)
        return filtered_data

    def can_filter(self):
        return self.config['language'] is not None
