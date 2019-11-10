__author__ = 'Nuullll'

from requests_html import HTMLSession
from pymongo import MongoClient
import datetime
import pandas as pd
import re

client = MongoClient()
db = client['leetcode_weekly']
members = db['members']


class Field(object):

    def __init__(self, name, selector='', cleaner=None):
        self.name = name
        self.selector = selector

        self.cleaner = Field.default_cleaner if cleaner is None else cleaner

    @staticmethod
    def default_cleaner(x):
        try:
            v = int(x.strip())
        except ValueError:
            v = x.strip()

        return v

    @staticmethod
    def fraction_cleaner(x):
        return [int(v.strip()) for v in x.split('/')]

    @staticmethod
    def percent_cleaner(x):
        return float(x.split('%')[0].strip()) / 100


class Parser(object):
    server_name = ''
    server_url = ''
    fields = []
    js_support = False
    today = str(datetime.date.today())

    @staticmethod
    def get_page(url, js_support=False):
        session = HTMLSession()
        r = session.get(url)
        if js_support:
            r.html.render(wait=5.0, timeout=15.0)

        ok = r.status_code == 200
        if ok:
            return ok, r.html

        return False, None

    @classmethod
    def get_user_url(cls, username):
        return cls.server_url + username

    @classmethod
    def parse_fields(cls, context):
        data = {}
        for field in cls.fields:
            raw = context.xpath(field.selector)

            try:
                cleaned = field.cleaner(raw[0])
                data[field.name] = cleaned
            except IndexError as e:
                print("WARNING: Failed to retrieve Field [{}] ({})".format(field.name, e))

        return data

    @classmethod
    def process_user(cls, alias, username):
        url = cls.get_user_url(username)

        ok, context = Parser.get_page(url, cls.js_support)
        if ok:
            data = cls.parse_fields(context)
            print("[{}@{}]: {}".format(username, cls.server_name, data))
            cls.export_user(alias, username, data)
        else:
            print("WARNING: Failed to get profile of [{}]".format(username))

    @classmethod
    def export_user(cls, alias, username, data):
        members.update_one(
            filter={'Alias': alias},
            update={
                '$set': {
                    cls.server_name + "." + username: {
                        cls.today: {
                            **data
                        },
                    }
                }
            },
            upsert=True
        )


class LeetcodeParser(Parser):
    server_name = 'leetcode'
    server_url = 'https://leetcode.com/'

    fields = [
        Field(
            'Solved Question',
            selector='//*[@id="base_content"]/div/div/div[1]/div[3]/ul/li[1]/span/text()',
            cleaner=Field.fraction_cleaner
        ),

        Field(
            'Finished Contests',
            selector='//*[@id="base_content"]/div/div/div[1]/div[2]/ul/li[1]/span/text()',
        ),

        Field(
            'Rating',
            selector='//*[@id="base_content"]/div/div/div[1]/div[2]/ul/li[2]/span/text()',
        ),

        Field(
            'Global Ranking',
            selector='//*[@id="base_content"]/div/div/div[1]/div[2]/ul/li[3]/span/text()',
            cleaner=Field.fraction_cleaner
        ),

        Field(
            'Accepted Submission',
            selector='//*[@id="base_content"]/div/div/div[1]/div[3]/ul/li[2]/span/text()',
            cleaner=Field.fraction_cleaner
        ),

        Field(
            'Acceptance Rate',
            selector='//*[@id="base_content"]/div/div/div[1]/div[3]/ul/li[3]/span/text()',
            cleaner=Field.percent_cleaner
        )
    ]


class LeetcodeCNParser(Parser):
    server_name = 'leetcode-cn'
    server_url = 'https://leetcode-cn.com/u/'
    js_support = True

    fields = [
        Field(
            'Solved Question',
            selector='//*[@id="lc-content"]/div/div/div[2]/div[2]/div[2]/div[4]/div[2]/span/text()',
            cleaner=Field.fraction_cleaner
        ),

        Field(
            'Finished Contests',
            selector='//*[@id="lc-content"]/div/div/div[2]/div[2]/div[2]/div[3]/p/text()',
            cleaner=lambda x: int(re.search(r'\d+', x)[0])
        ),

        Field(
            'Global Ranking',
            selector='//*[@id="lc-content"]/div/div/div[1]/div/div[1]/div/div[3]/span/text()'
        ),

        Field(
            'Accepted Submission',
            selector='//*[@id="lc-content"]/div/div/div[2]/div[2]/div[2]/div[4]/div[3]/span/text()',
            cleaner=Field.fraction_cleaner
        ),

        Field(
            'Acceptance Rate',
            selector='//*[@id="lc-content"]/div/div/div[2]/div[2]/div[2]/div[4]/div[4]/span/text()',
            cleaner=Field.percent_cleaner
        )
    ]


class LuoguParser(Parser):
    server_name = 'luogu'
    server_url = 'https://www.luogu.org/user/'
    js_support = True

    fields = [
        Field(
            'Solved Question',
            selector='//*[@id="app"]/div[2]/main/div/div[1]/div[2]/div[2]/div/div[4]/span[2]/text()',
        ),

        Field(
            'Submission',
            selector='//*[@id="app"]/div[2]/main/div/div[1]/div[2]/div[2]/div/div[3]/span[2]/text()'
        ),

        Field(
            'Ranking',
            selector='//*[@id="app"]/div[2]/main/div/div[1]/div[2]/div[2]/div/div[5]/span[2]/text()'
        )
    ]


if __name__ == '__main__':

    parsers = {
        'leetcode-cn': LeetcodeCNParser,
        'leetcode': LeetcodeParser,
        'luogu': LuoguParser
    }

    df = pd.read_csv('members.csv', keep_default_na=False)
    N = len(df)
    START, END = 24, N+1

    servers = df.columns[1:]
    for i, row in df[START:END].iterrows():
        print("Processing {}/{}".format(i+1, N))

        for server in servers:
            username = row[server]
            if username == '':
                continue

            parser = parsers[server]
            parser.process_user(row['群昵称'], username)
