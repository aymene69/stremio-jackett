from utils.filter.base_filter import BaseFilter
from utils.logger import setup_logger

logger = setup_logger(__name__)


class TitleExclusionFilter(BaseFilter):
    def __init__(self, config):
        super().__init__(config)

    def filter(self, data):
        filtered_items = []
        excluded_keywords = [keyword.upper() for keyword in self.config['exclusionKeywords']]
        for stream in data:
            for keyword in excluded_keywords:
                if keyword in stream.title.upper():
                    break
            else:
                filtered_items.append(stream)
        return filtered_items

    def can_filter(self):
        return self.config['exclusionKeywords'] is not None and len(self.config['exclusionKeywords']) > 0
