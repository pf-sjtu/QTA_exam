# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 11:24:21 2020

@author: PENG Feng
@email:  im.pengf@outlook.com
"""
import pandas as pd
from collections.abc import Iterable
import sys

from constants import DATA_DIR, TYPE_E, VALUE_E, BACK_TEST_MONTHS
from utils import str2date


class Stockprice(object):
    def __init__(
        self,
        data_dir: str = DATA_DIR,
        test: [bool, int] = False,
        # fill_daily_stockprice=None,
    ):
        # if fill_daily_stockprice is None:
        test_nrows = 1000
        if isinstance(test, int) and test > 0:
            test_nrows = test
            test = True
        df = pd.read_csv(data_dir, nrows=test_nrows if test else None)
        df.drop(columns=df.columns[0], inplace=True)
        df["time"] = pd.to_datetime(df["time"], format="%Y-%m-%d")
        df = df[df.isnull().sum(axis=1) != df.shape[1] - 2]
        self.data = df.sort_values(["time", "code"], ascending=True)
        self._back_test_wash()
        self._fill_daily_stockprice()
        # else:
        # self.data = self._fill_daily_stockprice(fill_daily_stockprice)

    def _back_test_wash(self):
        df = self.data
        key_dates = []
        for month in BACK_TEST_MONTHS:
            eval_date, adj_date = self.nearest_2_dates(month)
            key_dates.append(eval_date)
            key_dates.append(adj_date)
        df_valid_count = (
            df.loc[df["time"].isin(key_dates), :].groupby("code")["money"].count()
        )
        df_valid = df_valid_count == len(key_dates)
        df_invalid_code = df_valid.index[df_valid == False]
        df_invalid_idx = df.index[
            df["time"].isin(key_dates) & df["code"].isin(df_invalid_code)
        ]
        self.data = df.drop(index=df_invalid_idx)

    def _fill_daily_stockprice(self):
        # if not hasattr(sp, "data"):
        #     raise ValueError(VALUE_E.format(sys._getframe().f_code.co_name))
        # df = sp.data.reset_index()
        df = self.data.reset_index()
        df_fill = pd.DataFrame(
            index=pd.MultiIndex.from_product(
                (df["time"].unique(), df["code"].unique()), names=["time", "code"]
            )
        ).reset_index()
        df = df.merge(df_fill, how="outer", on=["time", "code"]).sort_values(
            ["time", "code"]
        )
        if df[["open", "close"]].isnull().sum(axis=0).sum() > 0:
            df[["open", "close"]] = df.groupby("code")[["open", "close"]].fillna(
                method="ffill"
            )
        if df[["open", "close"]].isnull().sum(axis=0).sum() > 0:
            df[["open", "close"]] = df.groupby("code")[["open", "close"]].fillna(
                method="bfill"
            )
        df["index"] = df["index"].fillna(df["index"].max() + 1).astype("int")
        df.set_index("index", inplace=True)
        self.data = df
        # return df

    def shape(self):
        return self.data.shape

    def stocks(self):
        return self.data["code"].drop_duplicates()

    def n_stocks(self):
        return self.stocks().shape[0]

    def columns(self):
        return self.data.columns

    def dates(self):
        return self.data["time"].drop_duplicates()

    def nearest_2_dates(self, date: str = "2020-08-01", geq=True):
        date = str2date(date)
        dates = self.dates()
        if geq:
            date1 = dates[dates < date].iloc[-1]
            date2 = dates[dates >= date].iloc[0]
        else:
            date1 = dates[dates <= date].iloc[-1]
            date2 = dates[dates > date].iloc[0]
        return date1, date2

    def code_fetch(self, codes: [str, list], on_code: bool = False):
        if isinstance(codes, str):
            return self.data[self.data["code"] == codes]
        elif isinstance((1, 2), Iterable):
            if on_code:
                idx = self.data.index
                df = self.data.set_index("code", drop=False)
                df["index"] = idx
                df = df.loc[codes, :].set_index("index")
            else:
                df = self.data[self.data["code"].isin(codes)]
            return df
        else:
            raise TypeError(TYPE_E.format(sys._getframe().f_code.co_name))

    def code_day_fetch(
        self, codes: [str, list], day: [int, list], on_code: bool = False
    ):
        df = self.code_fetch(codes=codes, on_code=on_code)
        codes = df["code"].drop_duplicates()
        if isinstance(day, int):
            day = (0, day)
        if isinstance(day, Iterable) and len(day) == 2:
            time_lists = df.groupby("code")["time"].agg(
                lambda x: list(x.drop_duplicates())
            )
            idx = pd.Index([])
            for code, time_list in zip(codes, time_lists):
                time_list = pd.Series(time_list)
                idx = idx.append(
                    df.index[
                        (df["code"] == code)
                        & (df["time"].isin(time_list[day[0] : day[1]]))
                    ]
                )
            return df.loc[idx, :]
        else:
            raise TypeError(TYPE_E.format(sys._getframe().f_code.co_name))

    def date_fetch(self, date: str = "2018-01-01"):
        date = str2date(date)
        return self.data[self.data["time"] == date]
