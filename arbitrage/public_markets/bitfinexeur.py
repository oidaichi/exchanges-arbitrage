# from arbitrage.public_markets._bitfinex import Bitfinex
from public_markets._bitfinex import Bitfinex
import config


class BitfinexEUR(Bitfinex):
    def __init__(self):
        coin = config.target_coin.lower()
        super().__init__("EUR", coin+"eur")
