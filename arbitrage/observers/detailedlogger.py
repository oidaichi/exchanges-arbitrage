import logging
# from arbitrage.observers.observer import Observer
from observers.observer import Observer
import config


class DetailedLogger(Observer):
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
            "profit: %.2f USD with volume: %.3f %s - buy at %.4f (%s) sell at %.4f (%s) ~%.2f%%"
            % (profit, volume, config.target_coin, buyprice, kask, sellprice, kbid, perc)
        )
