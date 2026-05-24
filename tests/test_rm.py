from pathlib import Path

import pytest

import gitlet


def test_remove_staged_file():
    file = Path("hello")
    file.write_text("hello")
    gitlet.main(["gitlet", "add", "hello"])
    gitlet.main(["gitlet", "rm", "hello"])
    assert file.exists()
    with pytest.raises(SystemExit):
        gitlet.main(["gitlet", "commit", "add hello"])


def test_remove_tracked_file():
    file = Path("hello")
    file.write_text("hello")
    gitlet.main(["gitlet", "add", "hello"])
    gitlet.main(["gitlet", "commit", "add hello"])
    gitlet.main(["gitlet", "rm", "hello"])
    assert not file.exists()


def test_remove_untracked_unstaged_file(capsys):
    file = Path("hello")
    file.write_text("hello")
    with pytest.raises(SystemExit):
        gitlet.main(["gitlet", "rm", "hello"])
    captured = capsys.readouterr()
    assert captured.err == "No reason to remove the file.\n"
    assert file.exists()
