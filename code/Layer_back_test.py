# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 22:30:11 2020

@author: PENG Feng
@email:  im.pengf@outlook.com
"""
import numpy as np
import pandas as pd
import sys
import os
import pickle
from matplotlib import pyplot as plt
from collections.abc import Iterable

from Stockprice import Stockprice
from utils import str2date, date2str
from constants import (
    BUFF_ALPHA_DIR,
    VALUE_E,
    N_MONEY_ADJ_ITER_A,
    N_MONEY_ADJ_ITER_B,
)


class Layer_back_test:
    @staticmethod
    def devide_weights(
        w: pd.Series, idx: pd.Index, alpha_series: pd.Series, n_layer: int
    ):
        a = alpha_series[idx]
        a_sorted = a.sort_values(ascending=True)
        w_sorted = w[a_sorted.index]
        w_sorted_cumsum = np.cumsum(w_sorted)
        layer_pcts = np.linspace(0, 1, n_layer + 1)
        layer_idx_dicts = []
        for i, layer_pct in enumerate(layer_pcts):
            if i == len(layer_pcts) - 2:
                index_lc = w_sorted_cumsum.index[w_sorted_cumsum >= layer_pct]
                index_l = index_lc[0]
                l_leak = w_sorted_cumsum[index_l] - w_sorted[index_l] < layer_pct
                layer_idx_dicts.append(
                    {
                        "pct": layer_pct,
                        "index_c": index_lc[1:] if l_leak else index_lc,
                        "index_l": index_l if l_leak else None,
                        "index_r": None,
                        "pct_l": w_sorted_cumsum[index_l] - layer_pct,
                        "pct_r": 0,
                    }
                )
            elif i == 0:
                index_lc = w_sorted_cumsum.index[
                    (w_sorted_cumsum >= layer_pct)
                    & (w_sorted_cumsum <= layer_pcts[i + 1])
                ]
                index_r = w_sorted_cumsum.index[w_sorted_cumsum > layer_pcts[i + 1]][0]
                r_leak = w_sorted_cumsum[index_r] > layer_pcts[i + 1]
                layer_idx_dicts.append(
                    {
                        "pct": layer_pct,
                        "index_c": index_lc,
                        "index_l": None,
                        "index_r": index_r if r_leak else None,
                        "pct_l": 0,
                        "pct_r": w_sorted[index_r]
                        - w_sorted_cumsum[index_r]
                        + layer_pcts[i + 1],
                    }
                )
            elif i != len(layer_pcts) - 1:
                index_lc = w_sorted_cumsum.index[
                    (w_sorted_cumsum >= layer_pct)
                    & (w_sorted_cumsum <= layer_pcts[i + 1])
                ]
                index_l = index_lc[0]
                index_r = w_sorted_cumsum.index[w_sorted_cumsum > layer_pcts[i + 1]][0]
                l_leak = w_sorted_cumsum[index_l] - w_sorted[index_l] < layer_pct
                r_leak = w_sorted_cumsum[index_r] > layer_pcts[i + 1]
                layer_idx_dicts.append(
                    {
                        "pct": layer_pct,
                        "index_c": index_lc[1:] if l_leak else index_lc,
                        "index_l": index_l if l_leak else None,
                        "index_r": index_r if r_leak else None,
                        "pct_l": w_sorted_cumsum[index_l] - layer_pct,
                        "pct_r": w_sorted[index_r]
                        - w_sorted_cumsum[index_r]
                        + layer_pcts[i + 1],
                    }
                )
        return layer_idx_dicts

    @staticmethod
    def alpha_series(
        sp: Stockprice, alpha_func, buff: bool = False, load_buff: bool = False,
    ):
        if load_buff and os.path.isfile(BUFF_ALPHA_DIR):
            with open(BUFF_ALPHA_DIR, "rb") as f:
                alpha_series = pickle.load(f)
            print('Loaded stock prices from: {}'.format(BUFF_ALPHA_DIR))
        else:
            alpha_series = sp.data.groupby("code").apply(alpha_func)
            alpha_series = alpha_series.reset_index()
            alpha_series.columns = ["code", "index", "alpha"]
            alpha_series = alpha_series.set_index("index")["alpha"]
            if buff or load_buff:
                with open(BUFF_ALPHA_DIR, "wb") as f:
                    pickle.dump(alpha_series, f)
                print('Dumped stock prices to: {}'.format(BUFF_ALPHA_DIR))
        return alpha_series

    @staticmethod
    def money_arr(layer_info_arr: Iterable):
        return [i["money_total"] for i in layer_info_arr]

    @staticmethod
    def buyin_info(
        sp: Stockprice,
        alpha_series: pd.Series,
        weight_func,
        n_layer: int,
        money_arr: Iterable,
        trade_tax_ratio: int = 0,
        eval_date: str = "2018-01-01",
        adj_date: str = "2018-01-01",
        layer_info_arr0: Iterable = None,
    ):
        w, idx = weight_func(sp, eval_date)
        layer_idx_dicts = Layer_back_test.devide_weights(w, idx, alpha_series, n_layer)
        buyin_code_arr = [
            sp.data.loc[i["index_c"], "code"].tolist() for i in layer_idx_dicts
        ]
        buyin_w_arr = [w.loc[i["index_c"]].tolist() for i in layer_idx_dicts]
        buyin_info_arr = []
        df_buyin_on_code = sp.data[sp.data["time"] == adj_date].set_index("code")
        if not layer_info_arr0 is None:
            buyin_n0_df = Layer_back_test.buyin_n_df(layer_info_arr0, sp=sp)[
                0
            ].set_index("code")
        for i in range(n_layer):
            index_l = layer_idx_dicts[i]["index_l"]
            index_r = layer_idx_dicts[i]["index_r"]
            w_l = layer_idx_dicts[i]["pct_l"]
            w_r = layer_idx_dicts[i]["pct_r"]
            if not index_l is None:
                buyin_code_arr[i] = [sp.data.loc[index_l, "code"]] + buyin_code_arr[i]
                buyin_w_arr[i] = [w_l] + buyin_w_arr[i]
            if not index_r is None:
                buyin_code_arr[i] = buyin_code_arr[i] + [sp.data.loc[index_r, "code"]]
                buyin_w_arr[i] = buyin_w_arr[i] + [w_r]
            buyin_money = np.array(buyin_w_arr[i]) * n_layer * money_arr[i]
            buyin_price = df_buyin_on_code.loc[buyin_code_arr[i], "close"]
            ##
            if not layer_info_arr0 is None:
                money_adj_total = 0
                if trade_tax_ratio != 0:
                    buyin_money0 = np.multiply(
                        buyin_n0_df.loc[buyin_code_arr[i], "n{}".format(i)], buyin_price
                    )
                    n_money_adj_iter = (
                        int(
                            N_MONEY_ADJ_ITER_A
                            * np.log10(money_arr[i] * trade_tax_ratio)
                        )
                        + N_MONEY_ADJ_ITER_B
                    )
                    for j in range(n_money_adj_iter):
                        stady_money = np.where(
                            buyin_money > buyin_money0, buyin_money0, buyin_money
                        )
                        money_adj = stady_money.sum() * trade_tax_ratio
                        money_adj_total += money_adj
                        buyin_money *= 1 + (money_adj / money_arr[i])
            ##
            buyin_price_tax = buyin_price * (1 + trade_tax_ratio)
            buyin_n = np.divide(buyin_money, buyin_price_tax)

            # floor
            buyin_n = np.floor(buyin_n)
            money_left = money_arr[i] - np.multiply(buyin_price_tax, buyin_n).sum()
            money_stock = np.multiply(buyin_price, buyin_n).sum()
            money_tax = np.multiply(buyin_price_tax - buyin_price, buyin_n).sum()
            if not layer_info_arr0 is None:
                money_left += money_adj_total
                money_tax -= money_adj_total

            buyin_info_arr.append(
                {
                    "money_total": money_arr[i],
                    "money_left": money_left,
                    "money_stock": money_stock,
                    "money_tax": money_tax,
                    "code": buyin_code_arr[i],
                    "weight": buyin_w_arr[i],
                    "n": buyin_n,
                    "price": buyin_price,
                    "price_tax": buyin_price_tax,
                    "money": buyin_money,
                    "eval_date": eval_date,
                    "adj_date": adj_date,
                }
            )
        return buyin_info_arr

    # @staticmethod
    # def buyin_money_df(layer_info_arr:list, df:pd=None, sp:Stockprice=None):
    #     money_left_arr = np.zeros(len(layer_info_arr))
    #     for i, info_dict in enumerate(layer_info_arr):
    #         money_left_arr[i] = info_dict["money_left"]
    #         n_col_name = "n{}".format(i)
    #         df_n = pd.DataFrame(
    #             {"code": info_dict["code"], n_col_name: info_dict["n"]}
    #         ).reset_index(drop=True)
    #         if df is None and not sp is None:
    #             date = layer_info_arr[0]['eval_date']
    #             df = sp.data[sp.data['time'] == date]
    #             df = pd.DataFrame(
    #                 index=pd.MultiIndex.from_product(
    #                     (df["time"].unique(), df["code"].unique()), names=["time", "code"]
    #                 )
    #             ).reset_index()
    #         elif df is None:
    #             raise ValueError(VALUE_E.format(sys._getframe().f_code.co_name))
    #         df = df.merge(df_n, how="left", on="code")
    #         df[n_col_name].fillna(0, inplace=True)
    #     return df, money_left_arr

    @staticmethod
    def buyin_n_df(layer_info_arr: Iterable, df: pd = None, sp: Stockprice = None):
        money_left_arr = np.zeros(len(layer_info_arr))
        for i, info_dict in enumerate(layer_info_arr):
            money_left_arr[i] = info_dict["money_left"]
            n_col_name = "n{}".format(i)
            df_n = pd.DataFrame(
                {"code": info_dict["code"], n_col_name: info_dict["n"]}
            ).reset_index(drop=True)
            if df is None and not sp is None:
                date = layer_info_arr[0]["eval_date"]
                df = sp.data[sp.data["time"] == date]
                df = pd.DataFrame(
                    index=pd.MultiIndex.from_product(
                        (df["time"].unique(), df["code"].unique()),
                        names=["time", "code"],
                    )
                ).reset_index()
            elif df is None:
                raise ValueError(VALUE_E.format(sys._getframe().f_code.co_name))
            df = df.merge(df_n, how="left", on="code")
            df[n_col_name].fillna(0, inplace=True)
        return df, money_left_arr

    @staticmethod
    def weighted_sum(
        sp: Stockprice,
        layer_info_arr: Iterable,
        date_beg: str = "2018-01-01",
        date_end: str = "2018-01-01",
        typ: str = "geq",  # leq geq eq neq
        price_typ: str = "close",  # open, close
    ):
        if not price_typ in ["open", "close"]:
            raise ValueError(VALUE_E.format(sys._getframe().f_code.co_name))
        date_beg = str2date(date_beg)
        date_end = str2date(date_end)
        df = sp.data
        if typ == "leq":
            s1 = df["time"] > date_beg
            s2 = df["time"] <= date_end
        elif typ == "geq":
            s1 = df["time"] >= date_beg
            s2 = df["time"] < date_end
        elif typ == "eq":
            s1 = df["time"] >= date_beg
            s2 = df["time"] <= date_end
        elif typ == "eq":
            s1 = df["time"] > date_beg
            s2 = df["time"] < date_end
        else:
            raise ValueError(VALUE_E.format(sys._getframe().f_code.co_name))
        df = df.loc[s1 & s2, ["time", "code", "open", "close"]]
        # not every stock apears everyday
        # merge number of stocks to price data
        df, money_left_arr = Layer_back_test.buyin_n_df(layer_info_arr, df)

        money_df = pd.DataFrame(
            {
                "money{}".format(i): df.groupby("time").apply(
                    lambda x: np.dot(x["n{}".format(i)], x[price_typ])
                )
                for i in range(len(layer_info_arr))
            }
        )
        money_df += money_left_arr
        return money_df

    @staticmethod
    def buyin_n_diff(
        sp: Stockprice, layer_info_arr1: Iterable, layer_info_arr2: Iterable,
    ):
        df1, money_left_arr1 = Layer_back_test.buyin_n_df(layer_info_arr1, sp=sp)
        df2, money_left_arr2 = Layer_back_test.buyin_n_df(layer_info_arr2, sp=sp)
        n_cols = [i for i in df1.columns if i not in ["time", "code"]]
        df1[n_cols] = df2[n_cols] - df1[n_cols]
        return df1

    @staticmethod
    def layer_money_series(
        sp: Stockprice,
        alpha_series: pd.Series,
        money_arr: Iterable,
        back_test_key_dates: Iterable,
        weight_func,
        n_layer: int,
        trade_tax_ratio: float,
    ):
        ptf_money = None
        buyin_info_arr0 = None
        layer_info_total = []
        for i, (eval_date, adj_date) in enumerate(back_test_key_dates[:-1]):
            print(
                "Running back test... ({}/{})".format(i, len(back_test_key_dates) - 2)
            )
            buyin_info_arr = Layer_back_test.buyin_info(
                sp=sp,
                alpha_series=alpha_series,
                weight_func=weight_func,
                n_layer=n_layer,
                money_arr=money_arr,
                trade_tax_ratio=trade_tax_ratio,
                eval_date=date2str(eval_date),
                adj_date=date2str(adj_date),
                layer_info_arr0=buyin_info_arr0,
            )
            layer_info_total.append(buyin_info_arr)
            ptf_money_total_df = Layer_back_test.weighted_sum(
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
        return ptf_money

    @staticmethod
    def portfolio_plot(
        ptf_money: pd.DataFrame, back_test_key_dates: Iterable = None, ax=None
    ):
        if ax is None:
            fig, ax = plt.subplots(figsize=(16, 8))
        for layer in range(ptf_money.shape[1]):
            s = ptf_money.iloc[:, layer]
            ax.plot(s.index, s, label="portfolio {}".format(layer))
        if not back_test_key_dates is None:
            for i, (eval_date, adj_date) in enumerate(back_test_key_dates[:-1]):
                ax.axvline(
                    x=adj_date,
                    color="grey",
                    linestyle="--",
                    label="warehouse transfer date" if i == 0 else None,
                )
        ax.legend(loc="upper right")
        ax.set_xlabel("Date")
        ax.set_ylabel("Close Price")
