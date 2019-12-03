
from checker.crawler import Runner


def test_runner_weekly():
    worker = Runner('Leetcode Weekly')

    worker.run_with_retry(force_update=False)


def test_runner_lc200():
    worker = Runner('Leetcode 200')

    worker.run_with_retry(force_update=True)
