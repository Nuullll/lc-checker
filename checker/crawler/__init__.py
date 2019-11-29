
from checker import settings
from checker.util import today
import importlib
import os
import pandas as pd


class Runner(object):

    def __init__(self):
        self._get_settings()

        self.members = None
        self.checked = set()
        self.date = today()

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
                    spider.process_user(alias, username)
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

    def _get_settings(self):

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
        self.members_file = os.path.join(self.data_dir, settings.MEMBERS_FILE)
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
                os.remove(os.path.join(root, file))

    def _recover_from_checkpoint(self):
        checkpoint = os.path.join(self.tmp_dir, '{}.cp'.format(self.date))

        if os.path.isfile(checkpoint):
            with open(checkpoint) as f:
                self.checked = {line.strip() for line in f.readlines()}
        else:
            self.checked = set()
            self._clean_tmp()

    def _load_members(self):
        self.members = pd.read_csv(self.members_file, keep_default_na=False)

    def _save_checkpoint(self, alias):
        checkpoint = os.path.join(self.tmp_dir, '{}.cp'.format(self.date))

        self.checked.add(alias)
        with open(checkpoint, 'a') as f:
            f.write(alias + '\n')
