# from arbitrage.public_markets._gdax import GDAX
from public_markets._gdax import GDAX
import config


class GDAXEUR(GDAX):
    def __init__(self):
        coin = config.target_coin.upper()
        super().__init__("EUR", coin+"-EUR")
