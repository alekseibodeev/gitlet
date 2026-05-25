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


def test_checkout_branch():
    file_a = Path("hello")
    file_a.write_text("hello")
    gitlet.main(["gitlet", "add", "hello"])
    gitlet.main(["gitlet", "commit", "add hello"])
    gitlet.main(["gitlet", "branch", "other"])
    gitlet.main(["gitlet", "rm", "hello"])
    file_b = Path("hola")
    file_b.write_text("hola")
    gitlet.main(["gitlet", "add", "hola"])
    gitlet.main(["gitlet", "commit", "remove hello and add hola"])
    gitlet.main(["gitlet", "checkout", "other"])
    assert file_a.exists() and file_a.read_text() == "hello"
    assert not file_b.exists()
    gitlet.main(["gitlet", "checkout", "master"])
    assert not file_a.exists()
    assert file_b.exists() and file_b.read_text() == "hola"


def test_checkout_unexisting_branch(capsys):
    with pytest.raises(SystemExit):
        gitlet.main(["gitlet", "checkout", "other"])
    captured = capsys.readouterr()
    assert captured.err == "No such branch exists.\n"


def test_checkout_current_branch(capsys):
    with pytest.raises(SystemExit):
        gitlet.main(["gitlet", "checkout", "master"])
    captured = capsys.readouterr()
    assert captured.err == "No need to checkout the current branch.\n"


def test_checkout_untracked_file_in_the_way(capsys):
    file = Path("hello")
    file.write_text("hello")
    gitlet.main(["gitlet", "branch", "other"])
    gitlet.main(["gitlet", "add", "hello"])
    gitlet.main(["gitlet", "commit", "add hello"])
    gitlet.main(["gitlet", "checkout", "other"])
    file.write_text("hola")
    with pytest.raises(SystemExit):
        gitlet.main(["gitlet", "checkout", "master"])
    captured = capsys.readouterr()
    assert (
        captured.err
        == "There is an untracked file in the way; delete it, or add and commmit it first.\n"
    )
