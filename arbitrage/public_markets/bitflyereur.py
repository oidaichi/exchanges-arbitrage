# from arbitrage.public_markets._bitflyer import BitFlyer
from public_markets._bitflyer import BitFlyer
import config


class BitFlyerEUR(BitFlyer):
    def __init__(self):
        coin = config.target_coin.upper()
        super().__init__("EUR", coin+"_EUR")
