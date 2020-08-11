# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 11:29:27 2020

@author: PENG Feng
@email:  im.pengf@outlook.com
"""
import time
import datetime
from pandas._libs.tslibs.timestamps import Timestamp


class Timer(object):
    def __enter__(self):
        self.t0 = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("[finished, spent time: {time:.2f}s]".format(time=time.time() - self.t0))


def str2date(date: str = "2020-08-01"):
    return datetime.datetime.strptime(date, "%Y-%m-%d")


def date2str(date: [datetime.datetime, Timestamp]):
    return datetime.datetime.strftime(date, "%Y-%m-%d")


def print_alpha_ans(df, date_beg: str = "2018-01-01", n_day: int = 10):
    print("{}:".format(df.name))
    date_beg = str2date(date_beg)
    df = df[df["time"] >= date_beg].iloc[:n_day, :]
    print(df)
    print("")


def date_arr_p1(date_arr):
    if date_arr[1] == 12:
        date_arr[0] += 1
        date_arr[1] = 1
    else:
        date_arr[1] += 1
    return date_arr


def date_str_p1(date_str):
    date_arr = date_str.split("-")[:2]
    date_arr = [int(i) for i in date_arr]
    date_arr = date_arr_p1(date_arr)
    date_str = "{}-{}-1".format(date_arr[0], date_arr[1])
    return date_str
