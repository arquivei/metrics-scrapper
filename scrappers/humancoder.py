from . import scrapper
from prometheus_client import Gauge
import requests

class HumanCoder(scrapper.Scrapper):
    URL = "http://fasttypers.org/imagepost.ashx"

    def __init__(self, prometheus_config):
        super(HumanCoder, self).__init__()

        self.balance = Gauge(
            "humancoder_balance",
            "Gives the current balance of the account",
            namespace=prometheus_config['namespace']
        )

    def scrapper(self, instance):
        payload = {
            "key": instance['key'],
            "action": "balance"
        }
        try:
            req = requests.post(
                self.URL,
                data=payload
            )
            if not req.text.isdigit():
                raise Exception("Unexpected return: {}".format(req.text))

            self.balance.set(int(req.text))
        except:
            pass