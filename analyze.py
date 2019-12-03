__author__ = 'Nuullll'

from pymongo import MongoClient
import datetime
import pandas as pd
import numpy as np
from operator import itemgetter
from checker.util import print_width

client = MongoClient()
db = client['leetcode_weekly']
members = db['members']
TODAY = str(datetime.date.today())


class Analyzer:

    servers = [
        'leetcode',
        'leetcode-cn',
        'luogu',
        'lintcode',
        'hdu',
        'vjudge'
    ]

    def __init__(self):
        documents = members.find({})
        self.data = self._clean(documents)
        self.merged_data = self.merge_columns()

    @staticmethod
    def _clean(documents):
        query_times = np.arange(np.datetime64(TODAY) - np.timedelta64(2, 'D'),
                                np.datetime64(TODAY) + np.timedelta64(1, 'D'))

        print("Time range: {}".format(query_times))

        cleaned = {}
        for doc in documents:
            name = doc['Alias']
            for server in Analyzer.servers:
                if server in doc:
                    ts = Analyzer.get_solved_question(doc[server], query_times)
                    cleaned[name + '@' + server] = ts

        return pd.DataFrame(cleaned)

    @staticmethod
    def get_solved_question(data, query_times):
        solved = []
        date_idx = []
        for username, frames in data.items():
            for date in query_times:
                date = date.__str__()
                if date in frames:
                    date_idx.append(date)
                    raw = frames[date]['Solved Question']

                    if isinstance(raw, list):
                        solved.append(raw[0])
                    elif isinstance(raw, int):
                        solved.append(raw)
                    else:
                        raise TypeError('Parse {} failed.'.format(raw))

        return pd.Series(solved, index=date_idx)

    def merge_columns(self):
        cols = self.data.columns
        merged = {}
        for col in cols:
            name = col.split('@')[0]
            if name in merged:
                merged[name] += self.data[col]
            else:
                merged[name] = self.data[col]

        return pd.DataFrame(merged)

    def delta(self, data=None):
        rank = []

        if data is None:
            data = self.merged_data

        cols = data.columns
        for col in cols:
            x = data[col].dropna().diff()
            count = x[x >= 0].sum()

            rank.append((col, count))

        rank.sort(reverse=True, key=itemgetter(1))

        return rank


if __name__ == '__main__':
    worker = Analyzer()

    rank = worker.delta()
    print('Platforms: {}'.format(worker.servers))

    max_width = 0
    for name, _ in rank:
        max_width = max(max_width, print_width(name))

    for i, item in enumerate(rank):
        name, c = item
        width = print_width(name)
        name = name + ' ' * (max_width - width + 1)
        print("| #{:<3}\t| {}\t| {:<4}\t|".format(i, name, int(c)))
