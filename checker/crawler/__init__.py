
from checker import settings
from checker.util import today
from pymongo import MongoClient
import importlib
import os
import pandas as pd

client = MongoClient()
db = client['oj_data']


class Runner(object):

    def __init__(self, group='Leetcode Weekly'):
        self._get_settings(group=group)

        self.group = group
        self.members = None
        self.checked = set()
        self.date = today()
        self.checkpoint = os.path.join(self.tmp_dir, '{}-{}.cp'.format(group, self.date))

        self.collection = db[group]

    def run_with_retry(self, retry=6, force_update=True):
        for i in range(retry):
            total, skip, success, fail = self.run_once(force_update)
            force_update = False
            if total == skip + success:
                print("Job finished. Retry = {}".format(i))
                return True

        return False

    def run_once(self, force_update=False):
        self._check_environment(force_update)
        self._load_members()

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
            for server in self.spiders.keys():
                if server not in servers:
                    continue

                username = row[server]
                if username == '':
                    continue

                spider = self.spiders[server]

                try:
                    data = spider.process_user(username)
                    if data:
                        self.export_item(alias, username, spider.server_name, data)

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

    def export_item(self, alias, username, server_name, data):
        self.collection.update_one(
            filter={'Alias': alias},
            update={
                '$set': {
                    server_name + "." + username + "." + self.date: {
                        **data
                    }
                }
            },
            upsert=True
        )

    def _get_settings(self, group):

        # platforms
        self.spiders = {}
        for server, spider in settings.PLATFORMS.items():
            mod_name, class_name = spider.split('.')
            m = importlib.import_module('.' + mod_name, 'checker.crawler.spiders')
            c = getattr(m, class_name)

            self.spiders[server] = c

        # tmp dir
        self._root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
        self.tmp_dir = os.path.join(self._root, settings.TMP_DIR)
        os.makedirs(self.tmp_dir, exist_ok=True)

        # data dir
        self.data_dir = os.path.join(self._root, settings.DATA_DIR)
        os.makedirs(self.data_dir, exist_ok=True)

        # members csv
        self.members_file = os.path.join(self.data_dir, settings.MEMBERS_FILE[group])
        if not os.path.isfile(self.members_file):
            raise FileNotFoundError('Members file not found: {}'.format(self.members_file))

    def _check_environment(self, force_update):
        self.date = today()

        if force_update:
            self.checked = set()
            self._clean_tmp()
        else:
            self._recover_from_checkpoint()

    def _clean_tmp(self):
        for root, _, files in os.walk(self.tmp_dir):
            for file in files:
                if file.startswith(self.group):
                    os.remove(os.path.join(root, file))

    def _recover_from_checkpoint(self):
        if os.path.isfile(self.checkpoint):
            with open(self.checkpoint) as f:
                self.checked = {line.strip() for line in f.readlines()}
        else:
            self.checked = set()
            self._clean_tmp()

    def _load_members(self):
        self.members = pd.read_csv(self.members_file, keep_default_na=False)

    def _save_checkpoint(self, alias):
        self.checked.add(alias)
        with open(self.checkpoint, 'a') as f:
            f.write(alias + '\n')
