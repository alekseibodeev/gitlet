import os

import pytest

import gitlet


@pytest.fixture(autouse=True)
def setup_repo(tmp_path):
    os.chdir(tmp_path)
    gitlet.main(["gitlet", "init"])
