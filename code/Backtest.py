# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 10:52:30 2020

@author: PENG Feng
@email:  im.pengf@outlook.com
"""
import numpy as np
import pandas as pd

from constants import (
    N_ANNUAL_TRADING_DAY,
    RISK_FREE_ANNUAL_RETURN_RATIO,
)


class Backtest:
    @staticmethod
    def _daily_return_ratio(ptf_money: pd.DataFrame):
        dr = ptf_money / ptf_money.shift(1) - 1
        return dr

    @staticmethod
    def return_ratio(ptf_money: pd.DataFrame):
        r = ptf_money.iloc[-1, :] / ptf_money.iloc[0, :]
        ar = r ** (N_ANNUAL_TRADING_DAY / (ptf_money.shape[0] - 1)) - 1
        return ar

    @staticmethod
    def volatility(ptf_money: pd.DataFrame):
        dr = Backtest._daily_return_ratio(ptf_money)
        dv = np.std(dr.iloc[1:, :], axis=0, ddof=0)
        av = dv * np.sqrt(N_ANNUAL_TRADING_DAY)
        return av

    @staticmethod
    def sharpe_ratio(ptf_money: pd.DataFrame):
        av = Backtest.volatility(ptf_money)
        ar = Backtest.return_ratio(ptf_money)
        asharp = (ar - RISK_FREE_ANNUAL_RETURN_RATIO) / av
        return asharp

    @staticmethod
    def information_ratio(ptf_money: pd.DataFrame):
        dr = Backtest._daily_return_ratio(ptf_money)
        d_risk_free_r = RISK_FREE_ANNUAL_RETURN_RATIO ** (1 / N_ANNUAL_TRADING_DAY)
        dr_surplus = dr - d_risk_free_r
        dt = np.std(dr_surplus.iloc[1:, :], axis=0, ddof=0)
        at = dt * np.sqrt(N_ANNUAL_TRADING_DAY)
        ar = Backtest.return_ratio(ptf_money)
        air = (ar - RISK_FREE_ANNUAL_RETURN_RATIO) / at
        return air

    @staticmethod
    def max_drawdown_ratio(ptf_money: pd.DataFrame):
        mdd = np.zeros((ptf_money.shape[1]))
        for i in range(ptf_money.shape[0] - 1):
            dd = (
                ptf_money.iloc[i + 1, :].max(axis=0) - ptf_money.iloc[i, :]
            ) / ptf_money.iloc[i, :]
            mdd = np.where(mdd > dd, dd, mdd)
        mdd = pd.Series(mdd, index=ptf_money.columns)
        return mdd

    @staticmethod
    def daily_winning_ratio(ptf_money: pd.DataFrame):
        dr = Backtest._daily_return_ratio(ptf_money)
        nw = (dr > 0).sum(axis=0)
        nl = (dr <= 0).sum(axis=0)
        dw = nw / (nw + nl)
        return dw

    @staticmethod
    def all_backtest(ptf_money: pd.DataFrame):
        backtests = [
            {"name": "annulized_return_ratio", "func": Backtest.return_ratio},
            {"name": "annulized_volatility", "func": Backtest.volatility},
            {"name": "annulized_sharpe_ratio", "func": Backtest.sharpe_ratio},
            {
                "name": "annulized_information_ratio",
                "func": Backtest.information_ratio,
            },
            {"name": "max_drawdown_ratio", "func": Backtest.max_drawdown_ratio},
            {"name": "daily_winning_ratio", "func": Backtest.daily_winning_ratio},
        ]
        for i, backtest in enumerate(backtests):
            if i == 0:
                backtest_result = pd.DataFrame(
                    {backtest["name"]: backtest["func"](ptf_money)}
                )
            else:
                backtest_result[backtest["name"]] = backtest["func"](ptf_money)
        backtest_result.index = range(ptf_money.shape[1])
        backtest_result.index.name = "portfolio"
        return backtest_result
