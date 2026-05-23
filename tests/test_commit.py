from pathlib import Path

import pytest

import gitlet


def test_commit_no_changes(capsys):
    file = Path("hello")
    file.write_text("hello")
    gitlet.main(["gitlet", "add", "hello"])
    gitlet.main(["gitlet", "commit", "add hello"])
    with pytest.raises(SystemExit):
        gitlet.main(["gitlet", "commit", "add hello again"])
    captured = capsys.readouterr()
    assert captured.err == "No changes added to the commit.\n"


def test_commit_blank_message(capsys):
    file = Path("hello")
    file.write_text("hello")
    gitlet.main(["gitlet", "add", "hello"])
    with pytest.raises(SystemExit):
        gitlet.main(["gitlet", "commit", "    "])
    captured = capsys.readouterr()
    assert captured.err == "Please enter a commit message.\n"
