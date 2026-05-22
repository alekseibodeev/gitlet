from datetime import datetime
import pickle
from hashlib import sha1
from typing import Any
from gitlet.blob import Blob
from gitlet.constants import COMMIT_DIR
from gitlet import index
from gitlet.error import CommitExistsException


class Commit:
    """Represents a Gitlet commit object.

    Commit is a combination of metadata (log message and timestamp), a referce
    to a tree (working diretory snapshot), and a reference to a parent commit(s).

    Attributes:
    id -- a SHA-1 hash of this commit
    message -- a short description of this commit
    timestamp -- date and time this commid was made
    parents -- a list of commits this commit was created from
    tracked -- an association between file names and blobs included to snapshot
    """

    def __init__(
        self,
        message: str,
        timestamp: datetime,
        parents: list[str],
        tracked: dict[str, Blob],
    ) -> None:
        self._id = None
        self.message = message
        self.timestamp = timestamp
        self.parents = parents
        self.tracked = tracked

    @property
    def id(self) -> str:
        if not self._id:
            self._id = sha1(self.serialize()).hexdigest()
        return self._id

    def serialize(self) -> bytes:
        return pickle.dumps(self)

    def dump(self) -> None:
        file = COMMIT_DIR / self.id
        file.write_bytes(self.serialize())

    @staticmethod
    def load(commit_id: str) -> Commit:
        file = COMMIT_DIR / commit_id
        if not file.exists():
            raise CommitExistsException()
        content = file.read_bytes()
        return pickle.loads(content)

    def __getstate__(self) -> dict[str, Any]:
        return {
            "message": self.message,
            "timestamp": self.timestamp,
            "parents": self.parents,
            "tracked": self.tracked,
        }

    def __setstate__(self, state: dict[str, Any]):
        self._id = None
        self.message = state["message"]
        self.timestamp = state["timestamp"]
        self.parents = state["parents"]
        self.tracked = state["tracked"]

    def commit(self, message: str) -> Commit:
        """Creates a new child commit."""
        tracked = {}
        for name, blob in self.tracked.items():
            if name in index.added or name in index.removed:
                continue
            tracked[name] = blob
        for name, blob in index.added.items():
            tracked[name] = blob
        return Commit(message, datetime.now(), [self.id], tracked)
