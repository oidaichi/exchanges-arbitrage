import logging
# from arbitrage.observers.observer import Observer
from observers.observer import Observer
import config


class Logger(Observer):
    def opportunity(
        self,
        profit,
        volume,
        buyprice,
        kask,
        sellprice,
        kbid,
        perc,
        weighted_buyprice,
        weighted_sellprice,
    ):
        logging.info(
            "profit: %.2f USD with volume: %.4f %s - buy from %s sell to %s ~%.2f%%"
            % (profit, volume, config.target_coin, kask, kbid, perc)
        )
