# from arbitrage.public_markets._btcc import BTCC
from public_markets._btcc import BTCC
import config


class BTCCCNY(BTCC):
    def __init__(self):
        coin = config.target_coin.lower()
        super().__init__("CNY", coin+"cny")
