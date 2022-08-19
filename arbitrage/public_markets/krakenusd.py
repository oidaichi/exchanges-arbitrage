# from arbitrage.public_markets._kraken import Kraken
from public_markets._kraken import Kraken
import config


class KrakenUSD(Kraken):
    def __init__(self):
        coin = config.target_coin.upper()
        if coin == 'BTC':
            coin = 'XBT'
        super().__init__("USD", f"X{coin}ZUSD")
