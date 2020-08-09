# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 17:15:43 2020

@author: PENG Feng
@email:  im.pengf@outlook.com
"""
from Stockprice import Stockprice


class Weights:
    @staticmethod
    def _delisted(sp: Stockprice, date: str = "2020-08-01"):
        df = sp.date_fetch(date)
        delisted = df["money"] == 0
        return delisted, df

    @staticmethod
    def equal(sp: Stockprice, date: str = "2020-08-01"):
        delisted, df = Weights._delisted(sp=sp, date=date)
        w = ~delisted / (~delisted).sum()
        w = w[w != 0]
        idx = df.index[~delisted]
        return w, idx

    @staticmethod
    def money(sp: Stockprice, date: str = "2020-08-01"):
        delisted, df = Weights._delisted(sp=sp, date=date)
        w = df["money"] / df["money"].sum()
        w = w[w != 0]
        idx = df.index[~delisted]
        return w, idx
