import os
import gitlet
import pytest


def test_init_basic(tmp_path):
    os.chdir(tmp_path)
    gitlet_dir = tmp_path / ".gitlet"
    gitlet.main(["gitlet", "init"])
    assert gitlet_dir.exists()


def test_init_repo_already_exist(tmp_path, capsys):
    os.chdir(tmp_path)
    gitlet.main(["gitlet", "init"])
    with pytest.raises(SystemExit):
        gitlet.main(["gitlet", "init"])
    _, err = capsys.readouterr()
    assert (
        err
        == "A Gitlet version-control system already exists in the current directory.\n"
    )
