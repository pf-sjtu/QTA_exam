# -*- coding: utf-8 -*-
"""
Created on Sun Aug  9 12:08:55 2020

@author: PENG Feng
@email:  im.pengf@outlook.com
"""
import numpy as np
import pandas as pd


t0 = pd.DataFrame(
    index=pd.MultiIndex.from_product(([1, 2], [4, 5]), names=["a", "b"])
).reset_index()
t1 = pd.DataFrame(
    index=pd.MultiIndex.from_product(([1, 2], [4, 5, 7]), names=["a", "b"])
).reset_index()
t0["index"] = range(2, t0.shape[0] + 2)
t0.set_index("index", inplace=True)
t0["c"] = range(t0.shape[0])
# t1['c'] = range(t1.shape[0])

t2 = t0.merge(t1, how="outer", on=["a", "b"])


t2.groupby(["a"])["c"].fillna(method="ffill", inplace=True)
# t3 = t2.groupby(['a'])['c'].fillna(method='ffill', inplace=False)


