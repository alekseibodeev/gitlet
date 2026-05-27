from pathlib import Path

import gitlet
from tests.definitions import parse_status_message


def test_status(capsys):
    a = Path("a")
    b = Path("b")
    c = Path("c")
    d = Path("d")
    e = Path("e")
    a.write_text("a")
    b.write_text("b")
    c.write_text("c")
    d.write_text("d")
    e.write_text("e")
    gitlet.main(["gitlet", "branch", "another"])
    gitlet.main(["gitlet", "branch", "other"])
    gitlet.main(["gitlet", "add", "a"])
    gitlet.main(["gitlet", "add", "b"])
    gitlet.main(["gitlet", "add", "c"])
    gitlet.main(["gitlet", "commit", "add a, b, c"])
    gitlet.main(["gitlet", "add", "d"])
    gitlet.main(["gitlet", "rm", "a"])
    b.write_text("bbbba")
    c.unlink()
    gitlet.main(["gitlet", "status"])
    captured = capsys.readouterr()
    [branches, staged, removed, modified, untracked] = parse_status_message(
        captured.out
    )
    assert branches == ["another", "*master", "other"]
    assert staged == ["d"]
    assert removed == ["a"]
    assert modified == ["b", "c"]
    assert untracked == ["e"]
