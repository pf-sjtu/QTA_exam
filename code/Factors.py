# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 11:32:11 2020

@author: PENG Feng
@email:  im.pengf@outlook.com
"""
import pandas as pd
import numpy as np
import sys

from constants import TYPE_E, VALUE_E
from Stockprice import Stockprice
from utils import str2date


class Factors:
    APPLY_FUNC_DICT = {sum: "sum", min: "min", max: "max"}
    APPLY_FUNC_STRS = [
        "count",
        "sum",
        "mean",
        "median",
        "var",
        "std",
        "skew",
        "kurt",
        "min",
        "max",
        "quantile",
        "corr",
        "cov",
    ]
    EWM_FUNC_DICT = {
        "a": "ewma",
        "mean": "ewma",
        "var": "ewmvar",
        "std": "ewmstd",
        "corr": "ewmcorr",
        "cov": "ewmcov",
    }

    @staticmethod
    def _date_clip(df: pd.DataFrame, n_day: int, date: str):
        date = str2date(date=date)
        idx_end = df.index[df["time"] == date]
        if len(idx_end) == 1:
            idx_end = idx_end[0]
            idx_beg = idx_end + 1 - n_day
        else:
            raise TypeError(TYPE_E.format(sys._getframe().f_code.co_name))
        df = df.loc[idx_beg:idx_end, :]
        return df

    @staticmethod
    def _window_apply_wash(
        sp: [Stockprice, pd.DataFrame, pd.Series],
        code: str = None,
        cols: [str, list] = None,
        n_day: int = 5,
        date: str = None,
    ):
        if isinstance(sp, Stockprice):
            df = sp.data
        elif isinstance(sp, pd.core.generic.NDFrame):
            df = sp
        else:
            raise TypeError(TYPE_E.format(sys._getframe().f_code.co_name))
        if not code is None:
            df = df[df["code"] == code]
        if not cols is None:
            df = df[cols]
        on_date = False
        if isinstance(date, str):
            on_date = True
            df = Factors._date_clip(df=df, n_day=n_day, date=date)
        return df, on_date

    @staticmethod
    def window_apply(
        func1d,
        sp: [Stockprice, pd.DataFrame, pd.Series],
        code: str = None,
        cols: [str, list] = None,
        n_day: int = 5,
        date: str = None,
        **kwargs,
    ):
        if n_day < 2 or not isinstance(n_day, int):
            raise ValueError(VALUE_E.format(sys._getframe().f_code.co_name))
        df, on_date = Factors._window_apply_wash(
            sp=sp, code=code, n_day=n_day, date=date
        )
        if func1d in Factors.APPLY_FUNC_DICT:
            func1d = Factors.APPLY_FUNC_DICT[func1d]
        df_rolling = df.rolling(window=n_day, min_periods=n_day, center=False)
        if func1d in Factors.APPLY_FUNC_STRS:
            df2 = eval("df_rolling.{}(**kwargs)".format(func1d))
        else:
            df2 = df_rolling.apply(func1d)
        if on_date:
            return df2.iloc[-1, :]
        else:
            return df2

    @staticmethod
    def ewm(
        func_ewm: str,
        sp: [Stockprice, pd.DataFrame, pd.Series],
        code: str = None,
        cols: [str, list] = None,
        **kwargs,
    ):
        df, _ = Factors._window_apply_wash(sp=sp, code=code, cols=cols)
        if func_ewm in Factors.EWM_FUNC_DICT:
            func_ewm = Factors.EWM_FUNC_DICT[func_ewm]
        df2 = eval("pd.{}(df, **kwargs)".format(func_ewm))
        return df2

    @staticmethod
    def series(
        sp: [Stockprice, pd.DataFrame, pd.Series],
        code: str = None,
        cols: [str, list] = None,
    ):
        df, _ = Factors._window_apply_wash(sp=sp, code=code, cols=cols)
        return df

    @staticmethod
    def mean(
        sp: [Stockprice, pd.DataFrame, pd.Series],
        n_day: int = 5,
        code: str = None,
        cols: [str, list] = None,
    ):
        return Factors.window_apply("mean", sp=sp, code=code, cols=cols, n_day=n_day)

    @staticmethod
    def delay(
        sp: [Stockprice, pd.DataFrame, pd.Series],
        n_day: int = 5,
        code: str = None,
        cols: [str, list] = None,
    ):
        df, _ = Factors._window_apply_wash(sp=sp, code=code, cols=cols)
        return df.shift(n_day)

    @staticmethod
    def count(
        df: [pd.DataFrame, pd.Series], n_day: int = 5,
    ):
        if (isinstance(df, pd.DataFrame) and df.dtypes.unique().tolist() == [bool]) or (
            isinstance(df, pd.Series) and df.dtypes == bool
        ):
            return Factors.window_apply(sum, sp=df, n_day=n_day)
        else:
            raise TypeError(TYPE_E.format(sys._getframe().f_code.co_name))

    @staticmethod
    def corr(
        s1: [list, np.array, pd.Series],
        s2: [list, np.array, pd.Series],
        n_day: int = 5,
    ):
        if not isinstance(s1, pd.Series):
            s1 = pd.Series(s1)
        if not isinstance(s2, pd.Series):
            s2 = pd.Series(s2)
        s1_rolling = s1.rolling(window=n_day, min_periods=n_day, center=False)
        s2_rolling = s2.rolling(window=n_day, min_periods=n_day, center=False)
        return s1_rolling.corr(s2_rolling)

    @staticmethod
    def alpha34(
        sp: Stockprice, code: str = None,
    ):
        close = Factors.series(sp, code, "close")
        return Factors.mean(close, 12) / close

    @staticmethod
    def alpha58(
        sp: Stockprice, code: str = None,
    ):
        close = Factors.series(sp, code, "close")
        return Factors.count(close > Factors.delay(close, 1), 20) / 20 * 100

    @staticmethod
    def alpha191(
        sp: Stockprice, code: str = None,
    ):
        volume = Factors.series(sp, code, "volume")
        low = Factors.series(sp, code, "low")
        high = Factors.series(sp, code, "high")
        close = Factors.series(sp, code, "close")
        return Factors.corr(Factors.mean(volume, 20), low, 5) + (high + low) / 2 - close
