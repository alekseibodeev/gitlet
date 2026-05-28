import pytest

import gitlet
from tests.definitions import parse_status_message


def test_rm_branch(capsys):
    gitlet.main(["gitlet", "branch", "other"])
    gitlet.main(["gitlet", "rm-branch", "other"])
    gitlet.main(["gitlet", "status"])
    captured = capsys.readouterr()
    branches, _, _, _, _ = parse_status_message(captured.out)
    assert len(branches) == 1


def test_rm_branch_no_branch_exists(capsys):
    with pytest.raises(SystemExit):
        gitlet.main(["gitlet", "rm-branch", "other"])
    captured = capsys.readouterr()
    assert captured.err == "No such branch exists.\n"


def test_rm_branch_current_branch(capsys):
    with pytest.raises(SystemExit):
        gitlet.main(["gitlet", "rm-branch", "master"])
    captured = capsys.readouterr()
    assert captured.err == "Cannot remove the current branch.\n"
