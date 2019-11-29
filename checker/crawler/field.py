# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Filename: field
# @Date: 2019-11-29-16-11
# @Author: Nuullll (Yilong Guo)
# @Email: vfirst218@gmail.com

from typing import Callable, Any

from checker.crawler.processor import JsonParser, Cleaner


class Field(object):
    """
    Abstraction of a xpath-selectable or json-parsable field on the webpages. A cleaner can also be bind to a Field.
    """
    def __init__(self, name: str, xpath_selector: str = '', json_parser: Callable[[dict], Any] = JsonParser.default,
                 cleaner: Callable[[str], Any] = Cleaner.default):
        self.name = name

        self.xpath_selector = xpath_selector
        self.json_parser = json_parser

        self.cleaner = cleaner
