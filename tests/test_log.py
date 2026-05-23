import re
from pathlib import Path

import gitlet
from tests.definitions import LOG


def test_log_init(capsys):
    gitlet.main(["gitlet", "log"])
    captured = capsys.readouterr()
    match = re.fullmatch(LOG, captured.out)
    assert match
    assert match.group("date") == "Thu Jan 01 00:00:00 1970"
    assert match.group("message") == "initial commit"


def test_log_two_commits(capsys):
    file = Path("hello")
    file.write_text("hello")
    gitlet.main(["gitlet", "add", "hello"])
    gitlet.main(["gitlet", "commit", "add hello"])
    file.write_text("hola")
    gitlet.main(["gitlet", "add", "hello"])
    gitlet.main(["gitlet", "commit", "add hola"])
    gitlet.main(["gitlet", "log"])
    captured = capsys.readouterr()
    matches = list(re.finditer(LOG, captured.out))
    assert len(matches) == 3
    assert matches[0].group("message") == "add hola"
    assert matches[1].group("message") == "add hello"
    assert matches[2].group("message") == "initial commit"
