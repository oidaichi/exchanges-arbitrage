# from arbitrage.public_markets._gemini import Gemini
from public_markets._gemini import Gemini
import config


class GeminiUSD(Gemini):
    def __init__(self):
        coin = config.target_coin.lower()
        super().__init__("USD", coin+"usd")
