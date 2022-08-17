# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

import time
import logging
import json
from concurrent.futures import ThreadPoolExecutor, wait
# from arbitrage import public_markets
# from arbitrage import observers
# from arbitrage import config
import public_markets
import observers
import config
from datetime import datetime
from functools import wraps


def time_recorder(func):
    @wraps(func)
    def new_function(*args, **kwargs):
        start_at = time.time()
        start_str = datetime.fromtimestamp(start_at).strftime('%Y-%m-%d %H:%I:%S')

        print('Started func:', func.__name__, '[' + start_str + ']')

        result = func(*args, **kwargs)

        end_at = time.time()
        end_str = datetime.fromtimestamp(end_at).strftime('%Y-%m-%d %H:%I:%S')
        time_taken = end_at - start_at

        print('Finished func:', func.__name__, 'took', '{:.3f}'.format(time_taken), 'sec[' + end_str + ']')

        return result
    return new_function


class Arbitrer(object):
    def __init__(self):
        self.markets = []
        self.observers = []
        self.depths = {}
        self.init_markets(config.markets)
        self.init_observers(config.observers)
        self.max_tx_volume = config.max_tx_volume
        self.threadpool = ThreadPoolExecutor(max_workers=10)

    def init_markets(self, markets):
        self.market_names = markets
        for market_name in markets:
            try:
                exec("import public_markets." + market_name.lower())
                market = eval(
                    "public_markets." + market_name.lower() + "." + market_name + "()"
                )
                self.markets.append(market)
            except (ImportError, AttributeError) as e:
                print(
                    "%s market name is invalid: Ignored (you should check your config file)"
                    % (market_name)
                )

    def init_observers(self, _observers):
        self.observer_names = _observers
        for observer_name in _observers:
            try:
                exec("import observers." + observer_name.lower())
                observer = eval(
                    "observers." + observer_name.lower() + "." + observer_name + "()"
                )
                self.observers.append(observer)
            except (ImportError, AttributeError) as e:
                print(
                    "%s observer name is invalid: Ignored (you should check your config file)"
                    % (observer_name)
                )
    
    def get_profit_for(self, mi, mj, kask, kbid):
        '''
        二つの取引所の間で価格差がある場合に使う。
        Returnの各値を求めて返す。

        Parameters
        ----------
        mi : int
            maxiのうち、現在処理しているi.
        mj : int
            maxjのうち、現在処理しているj.
        kask : str
            取引所の名前とUSDなどの通貨。ask側。
        kbid : str
            取引所の名前とUSDなどの通貨。bid側。

        Returns
        -------
        profit : float
            利益.
        sell_total : float
            売り注文を出す合計注文数.
        w_buyprice : float
            板に出ている買い注文数を重みとした購入価格の加重平均.
        w_sellprice : float
            板に出ている売り注文数を重みとした購入価格の加重平均.

        '''
        # ask側の方が価格が高ければ、裁定機会がないのでreturnする。
        if self.depths[kask]["asks"][mi]["price"] >= self.depths[kbid]["bids"][mj]["price"]:
            return 0, 0, 0, 0

        # 板気配とbuy側・sell側・設定した最大値から、購入する最大通貨量を求める
        max_amount_buy = 0
        for i in range(mi + 1):
            max_amount_buy += self.depths[kask]["asks"][i]["amount"]
        max_amount_sell = 0
        for j in range(mj + 1):
            max_amount_sell += self.depths[kbid]["bids"][j]["amount"]
        max_amount = min(max_amount_buy, max_amount_sell, self.max_tx_volume)

        buy_total = 0
        w_buyprice = 0
        for i in range(mi + 1):
            price = self.depths[kask]["asks"][i]["price"]
            amount = min(max_amount, buy_total + self.depths[kask]["asks"][i]["amount"]) - buy_total
            if amount <= 0:
                break
            buy_total += amount
            if w_buyprice == 0:
                w_buyprice = price
            else:
                w_buyprice = (w_buyprice * (buy_total - amount) + price * amount) / buy_total

        sell_total = 0
        w_sellprice = 0
        for j in range(mj + 1):
            price = self.depths[kbid]["bids"][j]["price"]
            amount = (
                min(max_amount, sell_total + self.depths[kbid]["bids"][j]["amount"]) - sell_total
            )
            if amount < 0:
                break
            sell_total += amount
            if w_sellprice == 0 or sell_total == 0:
                w_sellprice = price
            else:
                w_sellprice = (w_sellprice * (sell_total - amount) + price * amount) / sell_total

        profit = sell_total * w_sellprice - buy_total * w_buyprice
        return profit, sell_total, w_buyprice, w_sellprice
    
    # @time_recorder
    def get_max_depth(self, kask, kbid):
        '''
        二つの取引所の間で価格差がある場合に使う。
        取引所間の板で価格差があり、トレードできる可能性のある最大数を求める。
        ただし計算途中で時間が過ぎてトレードできなくなる可能性もあるため、あくまで最大値である。

        Parameters
        ----------
        kask : str
            取引所の名前とUSDなどの通貨。ask側。
        kbid : str
            取引所の名前とUSDなどの通貨。bid側。

        Returns
        -------
        i : int
            asksの何番目のインデックスまでbidsよりも価格が安いか
        j : int
            bidsの何番目のインデックスまでasksよりも価格が高いか

        '''
        i = 0
        # ask側とbid側の板にオーダーが入っている場合に処理を行う。
        if len(self.depths[kbid]["bids"]) != 0 and len(self.depths[kask]["asks"]) != 0:
            # asks、bids共にインデックスが若いほうが価格が安い。
            # asksの何番目のインデックスまでbidsより安いかを調べる。
            while self.depths[kask]["asks"][i]["price"] < self.depths[kbid]["bids"][0]["price"]:
                # カウンタがask側の板に出ている注文数より多くなったら終了。
                if i >= len(self.depths[kask]["asks"]) - 1:
                    break
                i += 1
        j = 0
        if len(self.depths[kask]["asks"]) != 0 and len(self.depths[kbid]["bids"]) != 0:
            # bidsの何番目までasksよりも価格が高いかを調べる。
            while self.depths[kask]["asks"][0]["price"] < self.depths[kbid]["bids"][j]["price"]:
                if j >= len(self.depths[kbid]["bids"]) - 1:
                    break
                j += 1
        return i, j

    # @time_recorder
    def arbitrage_depth_opportunity(self, kask, kbid):
        '''
        二つの取引所の間で価格差がある場合に使う。

        Parameters
        ----------
        kask : str
            取引所の名前とUSDなどの通貨.ask側。
        kbid : str
            取引所の名前とUSDなどの通貨。bid側。

        Returns
        -------
        best_profit : float
            利益が取れる見込みのある価格のうちの最高利益.
        best_volume : float
            最高利益の場合の取引量。
        float
            最高利益の場合の板上の買い価格.
        float
            最高利益の場合の板上の売り価格.
        best_w_buyprice : float
            最高利益の場合のエントリーする買い価格.
        best_w_sellprice : float
            最高利益の場合のエントリーする売り価格.

        '''
        # maxi: asksの何番目のインデックスまでbidsよりも価格が安いか
        # maxj: bidsの何番目のインデックスまでasksよりも価格が高いか
        maxi, maxj = self.get_max_depth(kask, kbid)
        best_profit = 0
        best_i, best_j = (0, 0)
        best_w_buyprice, best_w_sellprice = (0, 0)
        best_volume = 0
        print('maxi:', maxi, 'maxj:', maxj)
        for i in range(min(maxi + 1, 1500)):
            for j in range(min(maxj + 1, 1500)):
        # for i in range(maxi, max(-1, maxi-1000), -1):
        #     for j in range(maxj, max(-1, maxj-1000), -1):
                # volumeは売り注文数。買い注文数は返していない。
                profit, volume, w_buyprice, w_sellprice = self.get_profit_for(i, j, kask, kbid)
                # 板の注文ごとに利益を求め、最も利益が高くなるパラメータの組み合わせを求める。
                if profit >= 0 and profit >= best_profit:
                    best_profit = profit
                    best_volume = volume
                    best_i, best_j = (i, j)
                    best_w_buyprice, best_w_sellprice = (w_buyprice, w_sellprice)
        print('best_i:', best_i, 'best_j:', best_j)
        return (
            best_profit,
            best_volume,
            self.depths[kask]["asks"][best_i]["price"],
            self.depths[kbid]["bids"][best_j]["price"],
            best_w_buyprice,
            best_w_sellprice,
        )

    # @time_recorder
    def arbitrage_opportunity(self, kask, ask, kbid, bid):
        '''
        二つの取引所の間で価格差がある場合に使う。
        

        Parameters
        ----------
        kask : str
            取引所の名前とUSDなどの通貨.ask側。
        ask : float
            ask側の最新価格.
        kbid : str
            取引所の名前とUSDなどの通貨。bid側。
        bid : float
            bid側の最新価格.

        Returns
        -------
        None.
        returnはないが、observer.opportunity()に求めた変数を格納して終える。

        '''
        perc = (bid["price"] - ask["price"]) / bid["price"] * 100
        profit, volume, buyprice, sellprice, weighted_buyprice, weighted_sellprice = self.arbitrage_depth_opportunity(
            kask, kbid
        )
        if volume == 0 or buyprice == 0:
            return
        perc2 = (1 - (volume - (profit / buyprice)) / volume) * 100
        for observer in self.observers:
            observer.opportunity(
                profit,
                volume,
                buyprice,
                kask,
                sellprice,
                kbid,
                perc2,
                weighted_buyprice,
                weighted_sellprice,
            )

    def __get_market_depth(self, market, depths):
        depths[market.name] = market.get_depth()

    def update_depths(self):
        depths = {}
        futures = []
        for market in self.markets:
            # submitは第一引数で並列実行する関数を指定、第二、第三引数は第一引数の関数に渡す引数。
            futures.append(self.threadpool.submit(self.__get_market_depth, market, depths))
        wait(futures, timeout=20)
        return depths

    def tickers(self):
        for market in self.markets:
            logging.verbose("ticker: " + market.name + " - " + str(market.get_ticker()))

    def replay_history(self, directory):
        import os
        import json
        import pprint

        files = os.listdir(directory)
        files.sort()
        for f in files:
            depths = json.load(open(directory + "/" + f, "r"))
            self.depths = {}
            for market in self.market_names:
                if market in depths:
                    self.depths[market] = depths[market]
            self.tick()

    def tick(self):
        for observer in self.observers:
            observer.begin_opportunity_finder(self.depths)

        # すべての取引所の組み合わせで価格の大小関係を調べる。
        for kmarket1 in self.depths:
            for kmarket2 in self.depths:
                if kmarket1 == kmarket2:  # same market
                    continue
                market1 = self.depths[kmarket1]
                market2 = self.depths[kmarket2]
                if (
                    market1["asks"]
                    and market2["bids"]
                    and len(market1["asks"]) > 0
                    and len(market2["bids"]) > 0
                ):
                    if float(market1["asks"][0]["price"]) < float(market2["bids"][0]["price"]):
                        self.arbitrage_opportunity(
                            kmarket1, market1["asks"][0], kmarket2, market2["bids"][0]
                        )

        for observer in self.observers:
            observer.end_opportunity_finder()

    def loop(self):
        while True:
            self.depths = self.update_depths()
            self.tickers()
            self.tick()
            time.sleep(config.refresh_rate)
