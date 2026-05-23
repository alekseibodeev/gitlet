from pathlib import Path

import pytest

import gitlet


def test_init_basic():
    gitlet_dir = Path(".gitlet")
    assert gitlet_dir.exists()


def test_init_repo_already_exist(capsys):
    with pytest.raises(SystemExit):
        gitlet.main(["gitlet", "init"])
    _, err = capsys.readouterr()
    assert (
        err
        == "A Gitlet version-control system already exists in the current directory.\n"
    )
