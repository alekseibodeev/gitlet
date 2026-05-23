import re
from pathlib import Path

import pytest

import gitlet
from tests import definitions


def test_checkout_basic():
    file = Path("hello")
    file.write_text("hello")
    gitlet.main(["gitlet", "add", "hello"])
    gitlet.main(["gitlet", "commit", "add hello"])
    file.write_text("hola")
    gitlet.main(["gitlet", "checkout", "--", "hello"])
    assert file.read_text() == "hello"


def test_checkout_prev_commit(capsys):
    file = Path("hello")
    file.write_text("hello")
    gitlet.main(["gitlet", "add", "hello"])
    gitlet.main(["gitlet", "commit", "add hello"])
    file.write_text("hola")
    gitlet.main(["gitlet", "add", "hello"])
    gitlet.main(["gitlet", "commit", "add hola"])
    gitlet.main(["gitlet", "log"])
    captured = capsys.readouterr()
    matches = list(re.finditer(definitions.LOG, captured.out))
    commit_id = matches[1].group("id")
    gitlet.main(["gitlet", "checkout", commit_id, "--", "hello"])
    assert file.read_text() == "hello"


def test_checkout_file_does_not_exist(capsys):
    file = Path("hello")
    file.write_text("hello")
    gitlet.main(["gitlet", "add", "hello"])
    gitlet.main(["gitlet", "commit", "add hello"])
    with pytest.raises(SystemExit):
        gitlet.main(["gitlet", "checkout", "--", "world"])
    captured = capsys.readouterr()
    assert captured.err == "File does not exist in that commit.\n"


def test_checkout_commit_does_not_exist(capsys):
    file = Path("hello")
    file.write_text("hello")
    gitlet.main(["gitlet", "add", "hello"])
    gitlet.main(["gitlet", "commit", "add hello"])
    with pytest.raises(SystemExit):
        gitlet.main(
            [
                "gitlet",
                "checkout",
                "0000000000000000000000000000000000000000",
                "--",
                "world",
            ]
        )
    captured = capsys.readouterr()
    assert captured.err == "No commit with that id exists.\n"
