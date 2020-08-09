# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 20:09:30 2020

@author: PENG Feng
@email:  im.pengf@outlook.com
"""
import pandas as pd
import numpy as np

from utils import print_alpha_ans
from Stockprice import Stockprice as Sp
from Factors import Factors as F


if __name__ == "__main__":
    # In[1]
    print("-" * 10 + "第{}题".format(1) + "-" * 10)

    target_codes = ["300419.XSHE", "300053.XSHE", "300033.XSHE"]
    key_cols = ["code", "time", "open", "close", "high", "low"]

    sp = Sp()

    daily = sp.code_day_fetch(target_codes, 10)[key_cols]
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
