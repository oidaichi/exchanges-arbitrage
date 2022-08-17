# from arbitrage.public_markets._okcoin import OKCoin
from public_markets._okcoin import OKCoin
import config


class OKCoinCNY(OKCoin):
    def __init__(self):
        coin = config.target_coin.lower()
        super().__init__("CNY", coin+"_cny")
