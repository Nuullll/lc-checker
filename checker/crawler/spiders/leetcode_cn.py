
import re
from checker.crawler.spiders.base import Spider
from checker.crawler.field import Field
from checker.crawler.processor import Cleaner


class LeetcodeCnSpider(Spider):
    server_name = 'leetcode-cn'
    server_url = 'https://leetcode-cn.com/u/{}'
    js_support = True

    fields = [
        Field(
            name='Solved Question',
            xpath_selector='//*[@id="lc-content"]/div/div/div[2]/div[2]/div[2]/div[4]/div[2]/span/text()',
            cleaner=Cleaner.get_fraction
        ),

        Field(
            name='Finished Contests',
            xpath_selector='//*[@id="lc-content"]/div/div/div[2]/div[2]/div[2]/div[3]/p/text()',
            cleaner=lambda x: int(re.search(r'\d+', x)[0])
        ),

        Field(
            name='Global Ranking',
            xpath_selector='//*[@id="lc-content"]/div/div/div[1]/div/div[1]/div/div[3]/span/text()'
        ),

        Field(
            name='Accepted Submission',
            xpath_selector='//*[@id="lc-content"]/div/div/div[2]/div[2]/div[2]/div[4]/div[3]/span/text()',
            cleaner=Cleaner.get_fraction
        ),

        Field(
            name='Acceptance Rate',
            xpath_selector='//*[@id="lc-content"]/div/div/div[2]/div[2]/div[2]/div[4]/div[4]/span/text()',
            cleaner=Cleaner.get_percent
        )
    ]
