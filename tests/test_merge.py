import re
from pathlib import Path

import pytest

import gitlet
from gitlet.repository import get_conflict_message
from tests.definitions import LOG


@pytest.mark.skip_autouse
def test_merge_content():
    content1 = b"hello"
    content2 = b"world"
    expected = b"""\
<<<<<<< HEAD
hello=======
world>>>>>>>
"""
    result = get_conflict_message(content1, content2)
    assert result == expected


def test_merge_given_ancestor(capsys):
    file_a = Path("hello")
    file_a.write_text("hello")
    gitlet.main(["gitlet", "branch", "other"])
    gitlet.main(["gitlet", "add", "hello"])
    gitlet.main(["gitlet", "commit", "add hello"])
    gitlet.main(["gitlet", "merge", "other"])
    captured = capsys.readouterr()
    assert captured.out == "Given branch is an ancestor of the current branch.\n"


def test_merge_fast_forward(capsys):
    file_a = Path("hello")
    file_a.write_text("hello")
    gitlet.main(["gitlet", "branch", "other"])
    gitlet.main(["gitlet", "add", "hello"])
    gitlet.main(["gitlet", "commit", "add hello"])
    gitlet.main(["gitlet", "checkout", "other"])
    gitlet.main(["gitlet", "merge", "master"])
    captured = capsys.readouterr()
    assert captured.out == "Current branch fast-forwarded.\n"
    assert file_a.exists()


def test_merge_no_conflict():
    file_a = Path("a")
    file_a.write_text("aaa")
    file_b = Path("b")
    file_b.write_text("bbb")
    gitlet.main(["gitlet", "add", "a"])
    gitlet.main(["gitlet", "add", "b"])
    gitlet.main(["gitlet", "commit", "add a and b"])
    gitlet.main(["gitlet", "branch", "other"])
    gitlet.main(["gitlet", "rm", "a"])
    file_c = Path("c")
    file_c.write_text("ccc")
    gitlet.main(["gitlet", "add", "c"])
    gitlet.main(["gitlet", "commit", "add c and remove a"])
    gitlet.main(["gitlet", "checkout", "other"])
    gitlet.main(["gitlet", "rm", "b"])
    file_d = Path("d")
    file_d.write_text("ddd")
    gitlet.main(["gitlet", "add", "d"])
    gitlet.main(["gitlet", "commit", "add d and remove b"])
    gitlet.main(["gitlet", "checkout", "master"])
    gitlet.main(["gitlet", "merge", "other"])
    assert not file_a.exists()
    assert not file_b.exists()
    assert file_c.exists()
    assert file_d.exists()


def test_merge_conflict(capsys):
    file_a = Path("a")
    file_a.write_text("aaa")
    file_b = Path("b")
    file_b.write_text("bbb")
    file_c = Path("c")
    file_c.write_text("ccc")
    file_d = Path("d")
    file_d.write_text("ddd")
    gitlet.main(["gitlet", "add", "a"])
    gitlet.main(["gitlet", "add", "b"])
    gitlet.main(["gitlet", "add", "c"])
    gitlet.main(["gitlet", "commit", "add a, b and c"])
    gitlet.main(["gitlet", "branch", "other"])
    gitlet.main(["gitlet", "rm", "a"])
    file_b.write_text("aaa")
    gitlet.main(["gitlet", "add", "b"])
    file_c.write_text("ddd")
    gitlet.main(["gitlet", "add", "c"])
    gitlet.main(["gitlet", "add", "d"])
    gitlet.main(["gitlet", "commit", "message 1"])
    gitlet.main(["gitlet", "checkout", "other"])
    file_a.write_text("bbb")
    gitlet.main(["gitlet", "add", "a"])
    gitlet.main(["gitlet", "rm", "b"])
    file_c.write_text("eee")
    gitlet.main(["gitlet", "add", "c"])
    file_d.write_text("fff")
    gitlet.main(["gitlet", "add", "d"])
    gitlet.main(["gitlet", "commit", "message 2"])
    gitlet.main(["gitlet", "checkout", "master"])
    gitlet.main(["gitlet", "merge", "other"])
    captured = capsys.readouterr()
    assert captured.out == "Encountered a merge conflict.\n"
    assert file_a.exists()
    assert file_a.read_bytes() == get_conflict_message(b"", b"bbb")
    assert file_b.exists()
    assert file_b.read_bytes() == get_conflict_message(b"aaa", b"")
    assert file_c.exists()
    assert file_c.read_bytes() == get_conflict_message(b"ddd", b"eee")
    assert file_d.exists()
    assert file_d.read_bytes() == get_conflict_message(b"ddd", b"fff")
    gitlet.main(["gitlet", "log"])
    captured = capsys.readouterr()
    matches = list(re.finditer(LOG, captured.out))
    assert matches[0].group("message") == "Merged other into master."


def test_merge_uncommited_changes(capsys):
    gitlet.main(["gitlet", "branch", "other"])
    file_a = Path("a")
    file_a.write_text("aaa")
    gitlet.main(["gitlet", "add", "a"])
    with pytest.raises(SystemExit):
        gitlet.main(["gitlet", "merge", "other"])
    captured = capsys.readouterr()
    assert captured.err == "You have uncommited changes.\n"


def test_merge_no_branch_exist(capsys):
    with pytest.raises(SystemExit):
        gitlet.main(["gitlet", "merge", "other"])
    captured = capsys.readouterr()
    assert captured.err == "No such branch exists.\n"


def test_merge_itself(capsys):
    with pytest.raises(SystemExit):
        gitlet.main(["gitlet", "merge", "master"])
    captured = capsys.readouterr()
    assert captured.err == "Cannot merge a branch with itself.\n"


def test_merge_untracked_files_in_the_way(capsys):
    file_a = Path("hello")
    gitlet.main(["gitlet", "branch", "other"])
    gitlet.main(["gitlet", "checkout", "other"])
    file_a.write_text("hello")
    gitlet.main(["gitlet", "add", "hello"])
    gitlet.main(["gitlet", "commit", "add hello"])
    gitlet.main(["gitlet", "checkout", "master"])
    file_a = Path("hello")
    file_a.write_text("hola")
    with pytest.raises(SystemExit):
        gitlet.main(["gitlet", "merge", "other"])
    captured = capsys.readouterr()
    assert (
        captured.err
        == "There is an untracked file in the way; delete it, or add and commmit it first.\n"
    )
