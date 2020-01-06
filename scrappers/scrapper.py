import logging

class Scrapper:
    def __init__(self):
        self.logger = logging.getLogger()

    def scrapper(self, instance):
        raise NotImplementedError