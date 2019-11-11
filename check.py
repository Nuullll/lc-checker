__author__ = 'Nuullll'

from requests_html import HTMLSession
from pymongo import MongoClient
import datetime
import pandas as pd
import re
import os

client = MongoClient()
db = client['leetcode_weekly']
members = db['members']
TODAY = str(datetime.date.today())


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
            if data == {}:
                raise FileNotFoundError("ID error or Network error. No data was retrieved.")
            cls.export_user(alias, username, data)
        else:
            print("WARNING: Failed to get profile of [{}]".format(username))

    @classmethod
    def export_user(cls, alias, username, data):
        members.update_one(
            filter={'Alias': alias},
            update={
                '$set': {
                    cls.server_name + "." + username + "." + TODAY: {
                        **data
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


class Checker:
    parsers = {
        'leetcode': LeetcodeParser,
        'leetcode-cn': LeetcodeCNParser,
        'luogu': LuoguParser
    }

    tmp_dir = 'tmp'

    def __init__(self, members_csv, date=TODAY):
        self.members = pd.read_csv(members_csv, keep_default_na=False)
        self.checkpoint = '{}/{}.cp'.format(Checker.tmp_dir, date)
        self.checked = set()

    def run(self, force_update=False):
        if force_update:
            self._clean_tmp()
        else:
            if self._has_checkpoint():
                self.checked = self._recover()

        skip = 0
        success = 0
        fail = 0
        fail_reason = []

        total = len(self.members)
        servers = self.members.columns[1:]

        for i, row in self.members.iterrows():
            print("Processing {}/{}".format(i + 1, total))
            alias = row['群昵称']
            if alias in self.checked:
                skip += 1
                print("Skipped.")
                continue

            ok = True
            for server in servers:
                username = row[server]
                if username == '':
                    continue

                parser = self.parsers[server]

                try:
                    parser.process_user(alias, username)
                except Exception as e:
                    print("WARNING: Network timeout. Skipped to the next entry. ({})".format(e))
                    ok = False
                    fail_reason.append("[{}: {}@{}] {}".format(alias, username, server, e))

            if ok:
                success += 1
                self._save_checkpoint(alias)
            else:
                fail += 1

        print("SUMMARY:")
        print("Total = {}, Skip = {}, Success = {}, Fail = {}".format(total, skip, success, fail))
        for reason in fail_reason:
            print("\t" + reason)

        return total, skip, success, fail

    def _has_checkpoint(self):
        os.makedirs(Checker.tmp_dir, exist_ok=True)

        if os.path.isfile(self.checkpoint):
            return True

        self._clean_tmp()
        return False

    def _save_checkpoint(self, alias):
        self.checked.add(alias)
        with open(self.checkpoint, 'a') as f:
            f.write(alias + '\n')

    @staticmethod
    def _clean_tmp():
        for root, _, files in os.walk(Checker.tmp_dir):
            for file in files:
                os.remove(os.path.join(root, file))

    def _recover(self):
        with open(self.checkpoint) as f:
            return {line.strip() for line in f.readlines()}


if __name__ == '__main__':
    retry = 6

    worker = Checker('members.csv')
    for i in range(retry):
        total, skip, success, fail = worker.run(force_update=False)
        if total == skip + success:
            print("Job finished. Retry = {}".format(i))
            break
