from utils.filter.base_filter import BaseFilter
from utils.logger import setup_logger

logger = setup_logger(__name__)


class QualityExclusionFilter(BaseFilter):
    def __init__(self, config):
        super().__init__(config)

    RIPS = ["HDRIP", "BRRIP", "BDRIP", "WEBRIP", "TVRIP", "VODRIP", "HDRIP"]
    CAMS = ["CAM", "TS", "TC", "R5", "DVDSCR", "HDTV", "PDTV", "DSR", "WORKPRINT", "VHSRIP", "HDCAM"]

    def filter(self, data):
        filtered_items = []
        excluded_qualities = [quality.upper() for quality in self.config['exclusion']]
        rips = "RIPS" in excluded_qualities
        cams = "CAM" in excluded_qualities

        for stream in data:
            for quality in stream.parsed_data.quality:
                if quality.upper() in excluded_qualities:
                    break
                if rips and quality.upper() in self.RIPS:
                    break
                if cams and quality.upper() in self.CAMS:
                    break
                filtered_items.append(stream)
            else:
                if "Unknown" not in excluded_qualities:
                    filtered_items.append(stream)
        return filtered_items

    def can_filter(self):
        return self.config['exclusion'] is not None and len(self.config['exclusion']) > 0
