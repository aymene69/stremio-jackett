from utils.filter.base_filter import BaseFilter
from utils.logger import setup_logger

logger = setup_logger(__name__)


class MaxSizeFilter(BaseFilter):
    def __init__(self, config, additional_config=None):
        super().__init__(config, additional_config)

    def filter(self, data):
        filtered_data = []
        for torrent in data:
            if torrent.size <= self.config['maxSize']:
                filtered_data.append(torrent)
        return filtered_data

    def can_filter(self):
        return int(self.config['maxSize']) > 0 and self.item_type == 'movie'
