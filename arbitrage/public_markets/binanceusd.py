# from arbitrage.public_markets._binance import Binance
from public_markets._binance import Binance
import config


class BinanceUSD(Binance):
    def __init__(self):
        coin = config.target_coin.upper()
        super().__init__("USD", coin+"USDT")
