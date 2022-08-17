# from arbitrage.public_markets._bitstamp import Bitstamp
from public_markets._bitstamp import Bitstamp
import config


class BitstampUSD(Bitstamp):
    def __init__(self):
        coin = config.target_coin.lower()
        super().__init__("USD", coin+"usd")


if __name__ == "__main__":
    market = BitstampUSD()
    market.update_depth()
    print(market.get_ticker())
