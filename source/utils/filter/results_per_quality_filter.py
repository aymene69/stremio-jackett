from utils.filter.base_filter import BaseFilter
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ResultsPerQualityFilter(BaseFilter):
    def __init__(self, config):
        super().__init__(config)

    def filter(self, data):
        filtered_items = []
        resolution_count = {}
        for item in data:
            logger.info(f"Filtering by quality: {item.parsed_data.resolution}")
            for resolution in item.parsed_data.resolution:
                if resolution not in resolution_count:
                    resolution_count[resolution] = 1
                    filtered_items.append(item)
                else:
                    if resolution_count[resolution] < int(self.config['resultsPerQuality']):
                        resolution_count[resolution] += 1
                        filtered_items.append(item)
            else:
                filtered_items.append(item)

        return filtered_items

    def can_filter(self):
        return self.config['resultsPerQuality'] is not None and int(self.config['resultsPerQuality']) > 0
