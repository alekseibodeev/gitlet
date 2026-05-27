import os

import pytest

import gitlet
from gitlet import index


@pytest.fixture(autouse=True)
def setup_repo(request, tmp_path):
    if "skip_autouse" in request.keywords:
        # workaround for tests that don't need a Gitlet repository
        yield  # required for being consistent with general behavior
        return
    os.chdir(tmp_path)
    gitlet.main(["gitlet", "init"])
    yield tmp_path
    # index from previous test ruins the later one
    # so clean it up
    index.clear()
