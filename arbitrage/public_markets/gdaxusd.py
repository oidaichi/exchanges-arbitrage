# from arbitrage.public_markets._gdax import GDAX
from public_markets._gdax import GDAX
import config


class GDAXUSD(GDAX):
    def __init__(self):
        coin = config.target_coin.upper()
        super().__init__("USD", coin+"-USD")
