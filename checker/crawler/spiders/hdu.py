
from checker.crawler.spiders.base import Spider
from checker.crawler.field import Field


class HduSpider(Spider):
    server_name = 'hdu'
    server_url = 'http://acm.hdu.edu.cn/userstatus.php?user={}'

    fields = [
        Field(
            name='Solved Question',
            xpath_selector='/html/body/table/tr[4]/td/table/tr/td/table/tr[4]/td[2]/text()'
        ),

        Field(
            name='Global Ranking',
            xpath_selector='/html/body/table/tr[4]/td/table/tr/td/table/tr[2]/td[2]/text()',
        ),
    ]
