# from arbitrage.public_markets._bitflyer import BitFlyer
from public_markets._bitflyer import BitFlyer
import config


class BitFlyerUSD(BitFlyer):
    def __init__(self):
        coin = config.target_coin.upper()
        super().__init__("USD", coin+"_USD")
