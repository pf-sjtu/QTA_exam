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
from Layer_backtest import Layer_backtest as L
from Backtest import Backtest as B
from constants import (
    BACKTEST_MONTHS,
    FIG_DIR,
    LOG_DIR,
    PORTFOLIO_MONEY_DIR,
    PORTFOLIO_BACKTEST_DIR,
)

from utils import print_alpha_ans, q_title

##### SETTINGS BEGIN #####
## Q1
target_codes = ["300419.XSHE", "300053.XSHE", "300033.XSHE"]
key_cols = ["code", "time", "open", "close", "high", "low"]
n_output_line = 10

## Q2
alpha_date_beg = "2018-01-01"
n_alpha_line = 10

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

TEST_MODE = False
##### SETTINGS END #####


if __name__ == "__main__":
    log_text = ""

    # In[1]
    print(q_title(1))
    # takes 10s
    print("Please wait for about {} secs.".format(10), end="\r")

    sp = Sp(load_buff=TEST_MODE)
    daily = sp.code_day_fetch(target_codes, n_output_line)[key_cols]

    log_text += q_title(1) + "\n"
    log_text += "{}\n\n".format(daily)
    print("Answer is written to the log file.\n")

    # In[2]
    print(q_title(2))
    # takes 2s
    print("Please wait for about {} secs.".format(2), end="\r")

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

    log_text += q_title(2) + "\n"
    log_text += print_alpha_ans(s0_alpha34, alpha_date_beg, n_alpha_line, True)
    log_text += print_alpha_ans(s1_alpha58, alpha_date_beg, n_alpha_line, True)
    log_text += print_alpha_ans(s2_alpha191, alpha_date_beg, n_alpha_line, True)
    print("Answer is written to the log file.\n")

    # In[3]
    print(q_title(3))
    # takes 60s
    print("Please wait for about {} secs.".format(60), end="\r")

    alpha = alphas[alpha_i]["func"]
    weight = weights[weight_i]["func"]

    alpha_series = L.alpha_series(sp, alpha, load_buff=TEST_MODE)

    backtest_key_dates = []
    for month in BACKTEST_MONTHS:
        eval_date, adj_date = sp.nearest_2_dates(month)
        backtest_key_dates.append((eval_date, adj_date))

    money_arr = np.ones(n_layer) * layer_money_init
    ptf_money = L.layer_money_series(
        sp=sp,
        alpha_series=alpha_series,
        money_arr=money_arr,
        backtest_key_dates=backtest_key_dates,
        weight_func=weight,
        n_layer=n_layer,
        trade_tax_ratio=trade_tax_ratio,
    )
    ptf_money.to_csv(PORTFOLIO_MONEY_DIR, index=True)

    fig, ax = plt.subplots(figsize=(16, 8))
    L.portfolio_plot(ptf_money, backtest_key_dates, ax)
    fig_dir = FIG_DIR + "_({}_{}).pdf".format(
        alphas[alpha_i]["name"], weights[weight_i]["name"]
    )
    fig.savefig(
        fig_dir, bbox_inches="tight",
    )

    backtest_result = B.all_backtest(ptf_money)
    backtest_result.to_csv(PORTFOLIO_BACKTEST_DIR, index=True)

    log_text += q_title(3) + "\n"
    log_text += """SETTINGS:
\tNumber of layers = {}
\tWarehouse transfer = monthly
\tFactor = {}
\tWeight = {}
\tTrade tax ratio = {}
\tStart-up capital = {}\n\n""".format(
        n_layer,
        alphas[alpha_i]["name"],
        weights[weight_i]["name"],
        trade_tax_ratio,
        layer_money_init,
    )
    log_text += "Portfolio money data: {}\n".format(PORTFOLIO_MONEY_DIR)
    log_text += "Portfolio money figure: {}\n".format(fig_dir)
    log_text += "Backtest result: {}\n".format(PORTFOLIO_BACKTEST_DIR)
    print("Answer is written to the log file.")
    print("Log file path: {}".format(LOG_DIR))

    with open(LOG_DIR, "w") as f:
        f.write(log_text)
