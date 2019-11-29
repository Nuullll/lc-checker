
from checker.crawler.spiders.base import Spider
from checker.crawler.field import Field


class LintcodeSpider(Spider):
    server_name = 'lintcode'
    server_url = 'https://www.lintcode.com/api/accounts/{}/profile/?format=json'

    fields = [
        Field(
            name='Solved Question',
            json_parser=lambda x: [x['user_summary']['problem']['total_accepted'],
                                   x['user_summary']['problem']['total']]
        ),

        Field(
            name='AI Problem Submitted',
            json_parser=lambda x: [x['user_summary']['ai']['total_submitted'],
                                   x['user_summary']['ai']['total']]
        )
    ]
