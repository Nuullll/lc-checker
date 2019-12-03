
from checker.crawler import Runner


def test_runner():
    worker = Runner()

    worker.run_with_retry(force_update=False)
