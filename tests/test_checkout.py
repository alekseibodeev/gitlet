from pathlib import Path

import gitlet


def test_checkout_basic():
    file = Path("hello")
    file.write_text("hello")
    gitlet.main(["gitlet", "add", "hello"])
    gitlet.main(["gitlet", "commit", "add hello"])
    file.write_text("hola")
    gitlet.main(["gitlet", "checkout", "--", "hello"])
    assert file.read_text() == "hello"
