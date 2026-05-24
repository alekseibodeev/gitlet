import pytest

import gitlet


def test_checkout_file_does_not_exist(capsys):
    with pytest.raises(SystemExit):
        gitlet.main(["gitlet", "branch", "master"])
    captured = capsys.readouterr()
    assert captured.err == "A branch with that name already exists.\n"
