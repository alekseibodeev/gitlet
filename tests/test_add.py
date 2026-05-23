import pytest

import gitlet


def test_add_file_does_not_exist(capsys):
    with pytest.raises(SystemExit):
        gitlet.main(["gitlet", "add", "hello"])
    captured = capsys.readouterr()
    assert captured.err == "File does not exist.\n"
