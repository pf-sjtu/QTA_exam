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
from constants import BACK_TEST_MONTHS, FIG_DIR

import pickle

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
    {"name": "等权重", "func": W.equal},
    {"name": "市值加权", "func": W.money},
]

alpha = alphas[alpha_i]["func"]
weight = weights[weight_i]["func"]

# In[3.2]
# takes 25s

# alpha_series = L.alpha_series(sp, alpha)

# with open('../input/alpha_series.pickle', 'wb') as f:
#     pickle.dump(alpha_series, f)

with open("../input/alpha_series.pickle", "rb") as f:
    alpha_series = pickle.load(f)


# In[3.3]
back_test_key_dates = []
for month in BACK_TEST_MONTHS:
    eval_date, adj_date = sp.nearest_2_dates(month)
    back_test_key_dates.append((eval_date, adj_date))

# In[3.4]
money_arr = np.ones(n_layer) * layer_money_init
ptf_money = None
buyin_info_arr0 = None
layer_info_total = []
for i, (eval_date, adj_date) in enumerate(back_test_key_dates[:-1]):
    print(i)
    buyin_info_arr = L.buyin_info(
        sp=sp,
        alpha_series=alpha_series,
        weight_func=weight,
        n_layer=n_layer,
        money_arr=money_arr,
        trade_tax_pct=trade_tax_pct,
        eval_date=date2str(eval_date),
        adj_date=date2str(adj_date),
        layer_info_arr0=buyin_info_arr0,
    )
    layer_info_total.append(buyin_info_arr)
    ptf_money_total_df = L.weighted_sum(
        sp=sp,
        layer_info_arr=buyin_info_arr,
        date_beg=date2str(adj_date),
        date_end=date2str(back_test_key_dates[i + 1][1]),
        typ="eq",  # leq geq eq neq
        price_typ="close",
    )
    if ptf_money is None:
        ptf_money = ptf_money_total_df
        buyin_info_arr0 = buyin_info_arr
    else:
        ptf_money = pd.concat([ptf_money, ptf_money_total_df], axis=0)
    money_arr = ptf_money_total_df.iloc[-1, :]

# In[3.5]
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(20, 10))
for layer in range(n_layer):
    s = ptf_money.iloc[:, layer]
    ax.plot(s.index, s, label="portfolio{}".format(layer))
ax.legend(loc="upper right")

# money_df = sp.portfolio_simple_test_plot(
#     date_beg="2018-1-1",
#     date_end="2019-1-1",
#     weight_col="money",
#     money_init=1e6,
#     trade_tax_pct=trade_tax_pct,
#     ax=ax,
# )

ax.set_xlabel('Date')
ax.set_ylabel('Close Price')
fig.savefig(FIG_DIR + "_({}_{}).pdf".format(alphas[alpha_i]["name"], weights[weight_i]["name"]), bbox_inches='tight')

# In[3.5]
# if False:
#     import matplotlib.pyplot as plt

#     fig, ax = plt.subplots(figsize=(10, 5))
#     for code in sp.data.loc[sp.data["money"] > 1e10, "code"].unique():
#         # for code in sp.stocks()[:10]:
#         s = sp.code_fetch(code)[["time", "close"]].set_index("time")
#         # date_beg = s.index[s.index >= str2date('2018-1-1')][0]
#         # date_end = s.index[s.index >= str2date('2018-12-30')][0]
#         s = s.loc[
#             (s.index >= str2date("2018-1-1")) & (s.index <= str2date("2018-12-30")), :
#         ]
#         s /= s.iloc[0]
#         ax.plot(s.index, s, label=code)
#     ax.legend(loc="upper right")

# In[3.5]
