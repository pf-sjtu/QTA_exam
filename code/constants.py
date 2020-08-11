# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 11:25:38 2020

@author: PENG Feng
@email:  im.pengf@outlook.com
"""
from utils import date_str_p1
import os

if not os.path.isdir("../input"):
    os.makedirs("../input")
if not os.path.isdir("../output"):
    os.makedirs("../output")

TYPE_E = "{}: improper types or lengths of parameters."
VALUE_E = "{}: improper range of parameters."
DATA_DIR = "../input/stockprice.csv"
BUFF_SP_DIR = "../input/stockprice.pickle"
BUFF_ALPHA_DIR = "../input/alpha_series.pickle"
FIG_DIR = "../output/portfolio_backtest"
PORTFOLIO_MONEY_DIR = "../output/portfolio_money.csv"
PORTFOLIO_BACKTEST_DIR = "../output/portfolio_backtest.csv"
LOG_DIR = "../output/output.log"

BACKTEST_DATE_BEG = "2018-1-1"
BACKTEST_N_MONTH = 12
BACKTEST_MONTHS = []
for i in range(BACKTEST_N_MONTH + 1):
    BACKTEST_MONTHS.append(BACKTEST_DATE_BEG)
    BACKTEST_DATE_BEG = date_str_p1(BACKTEST_DATE_BEG)

N_MONEY_ADJ_ITER_A = 0.4
N_MONEY_ADJ_ITER_B = 1

N_ANNUAL_TRADING_DAY = 250

RISK_FREE_ANNUAL_RETURN_RATIO = 0.015
