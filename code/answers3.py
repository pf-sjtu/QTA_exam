# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 17:05:55 2020

@author: PENG Feng
@email:  im.pengf@outlook.com
"""
import numpy as np
import pandas as pd
import datetime

from Stockprice import Stockprice as Sp
from Factors import Factors as F
from Weights import Weights as W
from utils import Timer, date_str_p1, date2str, str2date
from Layer_back_test import Layer_back_test as L
from constants import BACK_TEST_MONTHS


# In[3.0]
sp = Sp()

# In[3.1]
alpha_i = 2
weight_i = 1
n_layer = 5
layer_money_init = 1e6
trade_tax_pct = 1e-4
# trade_tax_pct = 0

alphas = [
    {"name": "alpha34", "func": F.alpha34},
    {"name": "alpha58", "func": F.alpha58},
    {"name": "alpha191", "func": F.alpha191},
]

weights = [
    {"name": "等权重", "func": W.equal},
    {"name": "市值加权", "func": W.money},
]

alpha = alphas[alpha_i]["func"]
weight = weights[weight_i]["func"]

# In[3.2]
# takes 25s
alpha_series = L.alpha_series(sp, alpha)

# In[3.3]
back_test_key_dates = []
for month in BACK_TEST_MONTHS:
    eval_date, adj_date = sp.nearest_2_dates(month)
    back_test_key_dates.append((eval_date, adj_date))

# In[3.4]
money_arr = np.ones(n_layer) * layer_money_init
for i, (eval_date, adj_date) in enumerate([back_test_key_dates[0]]):
    buyin_info_arr = L.buyin_info(
        sp=sp,
        alpha_series=alpha_series,
        weight_func=weight,
        n_layer=n_layer,
        money_arr=money_arr,
        trade_tax_pct=trade_tax_pct,
        eval_date=date2str(eval_date),
        adj_date=date2str(adj_date),
    )
    ptf_money_df = L.weighted_sum(
        sp=sp,
        layer_info_arr=buyin_info_arr,
        date_beg=date2str(adj_date),
        date_end=date2str(back_test_key_dates[i+1][1]),
        typ="eq",  # leq geq eq neq
        price_typ="close",
    )

# In[3.5]
# sp_filled = Sp(fill_daily_stockprice=sp)
# In[3.5]
