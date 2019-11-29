
from checker.crawler.spiders.base import Spider
from checker.crawler.field import Field
from checker.crawler.processor import Cleaner


class LuoguSpider(Spider):
    server_name = 'luogu'
    server_url = 'https://www.luogu.org/user/{}'
    js_support = True

    fields = [
        Field(
            name='Solved Question',
            xpath_selector='//*[@id="app"]/div[2]/main/div/div[1]/div[2]/div[2]/div/div[4]/span[2]/text()',
            cleaner=Cleaner.get_fraction
        ),

        Field(
            name='Submission',
            xpath_selector='//*[@id="app"]/div[2]/main/div/div[1]/div[2]/div[2]/div/div[3]/span[2]/text()'
        ),

        Field(
            name='Ranking',
            xpath_selector='//*[@id="app"]/div[2]/main/div/div[1]/div[2]/div[2]/div/div[5]/span[2]/text()'
        )
    ]
