from utils.filter.base_filter import BaseFilter
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ResultsPerQualityFilter(BaseFilter):
    def __init__(self, config):
        super().__init__(config)

    def filter(self, data):
        filtered_items = []
        quality_count = {}
        for item in data:
            if item.quality not in quality_count:
                quality_count[item.quality] = 1
                filtered_items.append(item)
            else:
                if quality_count[item.quality] < int(self.config['resultsPerQuality']):
                    quality_count[item.quality] += 1
                    filtered_items.append(item)

        return filtered_items

    def can_filter(self):
        return self.config['resultsPerQuality'] is not None and int(self.config['resultsPerQuality']) > 0
