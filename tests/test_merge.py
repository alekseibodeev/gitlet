from pathlib import Path

import gitlet


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
