# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 17:05:55 2020

@author: PENG Feng
@email:  im.pengf@outlook.com
"""
import numpy as np
import matplotlib.pyplot as plt

from Stockprice import Stockprice as Sp
from Factors import Factors as F
from Weights import Weights as W
from Layer_back_test import Layer_back_test as L
from Back_test import Back_test as B
from constants import BACK_TEST_MONTHS, FIG_DIR

# In[3.0]
sp = Sp(buff=True, load_buff=True)


# In[3.1]
alpha_i = 2
weight_i = 1
n_layer = 5
# n_layer = 1
layer_money_init = 1e6
trade_tax_pct = 1e-4
# trade_tax_pct = 0

alphas = [
    {"name": "alpha34", "func": F.alpha34},
    {"name": "alpha58", "func": F.alpha58},
    {"name": "alpha191", "func": F.alpha191},
]

weights = [
    {"name": "equal", "func": W.equal},
    {"name": "capitalization", "func": W.money},
]

alpha = alphas[alpha_i]["func"]
weight = weights[weight_i]["func"]

# In[3.2]
# takes 25s
alpha_series = L.alpha_series(sp, alpha, buff=True, load_buff=True)

# In[3.3]
back_test_key_dates = []
for month in BACK_TEST_MONTHS:
    eval_date, adj_date = sp.nearest_2_dates(month)
    back_test_key_dates.append((eval_date, adj_date))

# In[3.4]
money_arr = np.ones(n_layer) * layer_money_init
ptf_money = L.layer_money_series(
    sp=sp,
    alpha_series=alpha_series,
    money_arr=money_arr,
    back_test_key_dates=back_test_key_dates,
    weight_func=weight,
    n_layer=n_layer,
    trade_tax_pct=trade_tax_pct,
)

# In[3.5]
fig, ax = plt.subplots(figsize=(16, 8))
L.portfolio_plot(ptf_money, back_test_key_dates, ax)
fig.savefig(
    FIG_DIR + "_({}_{}).pdf".format(alphas[alpha_i]["name"], weights[weight_i]["name"]),
    bbox_inches="tight",
)

# In[3.5]
back_test_result = B.all_back_test(ptf_money)
