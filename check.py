__author__ = 'Nuullll'

from requests_html import HTMLSession
from pymongo import MongoClient
import datetime
import pandas as pd

client = MongoClient()
db = client['leetcode_weekly']
members = db['members']


class Field(object):

    def __init__(self, name, selector='', cleaner=lambda x: x):
        self.name = name
        self.selector = selector
        self.cleaner = cleaner


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
            r.html.render()

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
            except Exception as e:
                print("WARNING: Failed to retrieve Field [{}] ({})".format(field.name, e))
                pass

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
                '$push': {
                    cls.server_name: {
                        'Timestamp': cls.today,
                        'Username': username,
                        **data
                    }
                }
            },
            upsert=True
        )


class LeetcodeParserEN(Parser):
    server_name = 'leetcode-en'
    server_url = 'https://leetcode.com/'

    fields = [
        Field(
            'Solved Question',
            selector='//*[@id="base_content"]/div/div/div[1]/div[3]/ul/li[1]/span/text()',
            cleaner=lambda x: x.split('/')[0].strip()
        ),
    ]


class LeetcodeParserZH(Parser):
    server_name = 'leetcode-zh'
    server_url = 'https://leetcode-cn.com/u/'
    js_support = True

    fields = [
        Field(
            'Solved Question',
            selector='//*[@id="lc-content"]/div/div/div[2]/div[2]/div[2]/div[4]/div[2]/span/text()',
            cleaner=lambda x: x.split('/')[0].strip()
        )
    ]


if __name__ == '__main__':
    parsers = {
        '国服': LeetcodeParserZH,
        '美服': LeetcodeParserEN
    }

    df = pd.read_csv('members.csv')
    N = len(df)

    for i, row in df.iterrows():
        print("Processing {}/{}".format(i+1, N))

        alias, username, server = row['群昵称'], row['Leetcode ID'], row['服务器']

        parser = parsers[server]
        parser.process_user(alias, username)
