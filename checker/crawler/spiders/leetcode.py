# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Filename: leetcode
# @Date: 2019-11-29-17-23
# @Author: Nuullll (Yilong Guo)
# @Email: vfirst218@gmail.com

from checker.crawler.spiders.base import Spider
from checker.crawler.field import Field
from checker.crawler.processor import Cleaner


class LeetcodeSpider(Spider):
    server_name = 'leetcode'
    server_url = 'https://leetcode.com/{}'

    fields = [
        Field(
            name='Solved Question',
            xpath_selector='//*[@id="base_content"]/div/div/div[1]/div[3]/ul/li[1]/span/text()',
            cleaner=Cleaner.get_fraction
        ),

        Field(
            name='Finished Contests',
            xpath_selector='//*[@id="base_content"]/div/div/div[1]/div[2]/ul/li[1]/span/text()',
        ),

        Field(
            name='Rating',
            xpath_selector='//*[@id="base_content"]/div/div/div[1]/div[2]/ul/li[2]/span/text()',
        ),

        Field(
            name='Global Ranking',
            xpath_selector='//*[@id="base_content"]/div/div/div[1]/div[2]/ul/li[3]/span/text()',
            cleaner=Cleaner.get_fraction
        ),

        Field(
            name='Accepted Submission',
            xpath_selector='//*[@id="base_content"]/div/div/div[1]/div[3]/ul/li[2]/span/text()',
            cleaner=Cleaner.get_fraction
        ),

        Field(
            name='Acceptance Rate',
            xpath_selector='//*[@id="base_content"]/div/div/div[1]/div[3]/ul/li[3]/span/text()',
            cleaner=Cleaner.get_percent
        )
    ]
