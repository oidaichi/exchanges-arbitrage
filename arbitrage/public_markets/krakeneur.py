# from arbitrage.public_markets._kraken import Kraken
from public_markets._kraken import Kraken
import config


class KrakenEUR(Kraken):
    def __init__(self):
        coin = config.target_coin.upper()
        if coin == 'BTC':
            coin = 'XBT'
        super().__init__("EUR", f"X{coin}ZEUR")
        # super().__init__("EUR", "XXBTZEUR")
