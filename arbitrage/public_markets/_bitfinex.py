import urllib.request
import urllib.error
import urllib.parse
import json
import logging
# from arbitrage.public_markets.market import Market
from public_markets.market import Market


class Bitfinex(Market):
    def __init__(self, currency, code):
        super().__init__(currency)
        self.code = code
        self.update_rate = 20        
        
    def update_depth(self):
        url = "https://api.bitfinex.com/v1/book/" + self.code
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
        req = urllib.request.Request(url, None, headers, method='GET')
        res = urllib.request.urlopen(req)
        try:
            depth = json.load(res)
        except Exception:
            logging.error("%s - Can't parse json: %s" % (self.name, res))
        self.depth = self.format_depth(depth)

    def sort_and_format(self, l, reverse=False):
        l.sort(key=lambda x: float(x["price"]), reverse=reverse)
        r = []
        for i in l:
            r.append({"price": float(i["price"]), "amount": float(i["amount"])})
        return r

    def format_depth(self, depth):
        bids = self.sort_and_format(depth["bids"], True)
        asks = self.sort_and_format(depth["asks"], False)
        return {"asks": asks, "bids": bids}
