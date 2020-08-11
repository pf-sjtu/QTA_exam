# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 20:09:30 2020

@author: PENG Feng
@email:  im.pengf@outlook.com
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from Stockprice import Stockprice as Sp
from Factors import Factors as F
from Weights import Weights as W
from Layer_back_test import Layer_back_test as L
from Back_test import Back_test as B
from constants import BACK_TEST_MONTHS, FIG_DIR

from utils import print_alpha_ans

##### SETTINGS BEGIN #####
## Q1
target_codes = ["300419.XSHE", "300053.XSHE", "300033.XSHE"]
key_cols = ["code", "time", "open", "close", "high", "low"]
n_output_line = 10

## Q2

## Q3
alpha_i = 2
weight_i = 1
n_layer = 5
# n_layer = 1
layer_money_init = 1e6
trade_tax_ratio = 1e-4
# trade_tax_ratio = 0

alphas = [
    {"name": "alpha34", "func": F.alpha34},
    {"name": "alpha58", "func": F.alpha58},
    {"name": "alpha191", "func": F.alpha191},
]

weights = [
    {"name": "equal", "func": W.equal},
    {"name": "capitalization", "func": W.money},
]

##### SETTINGS END #####


if __name__ == "__main__":
    # In[1]
    print("-" * 10 + "第{}题".format(1) + "-" * 10)

    # takes 10s
    sp = Sp(load_buff=True)
    daily = sp.code_day_fetch(target_codes, n_output_line)[key_cols]
    print(daily)

    # In[2]
    print("-" * 10 + "第{}题".format(2) + "-" * 10)

    s0_alpha34 = pd.DataFrame(
        {
            "time": F.series(sp, target_codes[0], "time"),
            "alpha34": F.alpha34(sp, target_codes[0]),
        }
    )
    s0_alpha34.name = "alpha34 of {}".format(target_codes[0])

    s1_alpha58 = pd.DataFrame(
        {
            "time": F.series(sp, target_codes[1], "time"),
            "alpha58": F.alpha58(sp, target_codes[1]),
        }
    )
    s1_alpha58.name = "alpha58 of {}".format(target_codes[1])

    s2_alpha191 = pd.DataFrame(
        {
            "time": F.series(sp, target_codes[2], "time"),
            "alpha191": F.alpha191(sp, target_codes[2]),
        }
    )
    s2_alpha191.name = "alpha191 of {}".format(target_codes[2])

    print_alpha_ans(s0_alpha34)
    print_alpha_ans(s1_alpha58)
    print_alpha_ans(s2_alpha191)

    # In[3]
    print("-" * 10 + "第{}题".format(3) + "-" * 10)

    alpha = alphas[alpha_i]["func"]
    weight = weights[weight_i]["func"]

    # takes 25s
    alpha_series = L.alpha_series(sp, alpha, load_buff=True)

    back_test_key_dates = []
    for month in BACK_TEST_MONTHS:
        eval_date, adj_date = sp.nearest_2_dates(month)
        back_test_key_dates.append((eval_date, adj_date))

    money_arr = np.ones(n_layer) * layer_money_init
    ptf_money = L.layer_money_series(
        sp=sp,
        alpha_series=alpha_series,
        money_arr=money_arr,
        back_test_key_dates=back_test_key_dates,
        weight_func=weight,
        n_layer=n_layer,
        trade_tax_ratio=trade_tax_ratio,
    )

    fig, ax = plt.subplots(figsize=(16, 8))
    L.portfolio_plot(ptf_money, back_test_key_dates, ax)
    fig.savefig(
        FIG_DIR
        + "_({}_{}).pdf".format(alphas[alpha_i]["name"], weights[weight_i]["name"]),
        bbox_inches="tight",
    )

    back_test_result = B.all_back_test(ptf_money)
