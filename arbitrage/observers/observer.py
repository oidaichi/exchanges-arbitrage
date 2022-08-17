import abc


class Observer(object, metaclass=abc.ABCMeta):
    def begin_opportunity_finder(self, depths):
        pass

    def end_opportunity_finder(self):
        pass

    
    ## abstract
    '''
    抽象クラスとはクラスの一種で、次の特徴を持つ抽象的な概念です。
    1. 専ら他のクラスに継承されることによって使用される。
    2. インスタンスを持たない。
    '''
    @abc.abstractmethod
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
        pass
