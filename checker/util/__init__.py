# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Filename: __init__.py
# @Date: 2019-11-29-17-21
# @Author: Nuullll (Yilong Guo)
# @Email: vfirst218@gmail.com

import datetime
import re


def today():
    return str(datetime.date.today())


def print_width(s):
    """
    Calculate the print width of string `s` on the console.
    """
    x = len(s)
    y = len(re.sub(r'[^\u0001-\u007f]+', r'', s))

    return 2 * x - y
