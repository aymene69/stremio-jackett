class BaseFilter:
    def __init__(self, config, additional_config=None):
        self.config = config
        self.item_type = additional_config

    def filter(self, data):
        raise NotImplementedError

    def can_filter(self):
        raise NotImplementedError

    def __call__(self, data):
        if self.config is not None and self.can_filter():
            return self.filter(data)
        return data
