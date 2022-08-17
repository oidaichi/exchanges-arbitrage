# from arbitrage.public_markets._bitstamp import Bitstamp
from public_markets._bitstamp import Bitstamp
import config


class BitstampEUR(Bitstamp):
    def __init__(self):
        coin = config.target_coin.lower()
        super().__init__("EUR", coin+"eur")


if __name__ == "__main__":
    market = BitstampEUR()
    market.update_depth()
    print(market.get_ticker())
