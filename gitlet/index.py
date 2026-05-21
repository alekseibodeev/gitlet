"""Represents a Gitlet staging area.

Staging area (or INDEX) is a temporary persistent storage for files that will
be added or removed on the next successful commit command.
"""

import pickle
from gitlet.blob import Blob
from gitlet.constants import INDEX_FILE


added: dict[str, Blob] = {}
removed: set[str] = set()


def serialize() -> bytes:
    return pickle.dumps((added, removed))


def dump() -> None:
    INDEX_FILE.write_bytes(serialize())


def load() -> None:
    global added, removed
    content = INDEX_FILE.read_bytes()
    added, removed = pickle.loads(content)
