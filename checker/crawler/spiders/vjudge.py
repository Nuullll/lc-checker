
from checker.crawler.spiders.base import Spider
from checker.crawler.field import Field


class VjudgeSpider(Spider):
    server_name = 'vjudge'
    server_url = 'https://vjudge.net/user/{}'

    fields = [
        Field(
            name='Solved Question',
            xpath_selector='/html/body/div[1]/div[1]/div[3]/table/tr[4]/td/a/text()'
        ),
    ]
