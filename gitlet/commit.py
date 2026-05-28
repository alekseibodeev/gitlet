import pickle
from collections import deque
from datetime import datetime
from hashlib import sha1
from typing import Any

from gitlet import index
from gitlet.blob import Blob
from gitlet.constants import COMMIT_DIR, WORKING_DIR
from gitlet.error import CommitExistsException
from gitlet.graph import Graph


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

    def __eq__(self, other) -> bool:
        if not isinstance(other, Commit):
            return NotImplemented
        return self.id == other.id

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

    def history(self) -> list[Commit]:
        """Returns a list of commits that is a commit history."""
        commits = []
        current_commit = self
        while current_commit.parents:
            commits.append(current_commit)
            current_commit = Commit.load(current_commit.parents[0])
        commits.append(current_commit)
        return commits

    def history2(self) -> list[Commit]:
        """Returns a list of commits by following all parent links."""
        commits: list[Commit] = []
        queue: deque[Commit] = deque([self])
        visited: set[str] = set([self.id])
        while queue:
            current_commit = queue.popleft()
            commits.append(current_commit)
            for parent_id in self.parents:
                parent = Commit.load(parent_id)
                if parent.id not in visited:
                    queue.append(parent)
                    visited.add(parent.id)
        return commits

    def __str__(self) -> str:
        s = self.timestamp.strftime("%a %b %d %H:%M:%S %Y")
        return f"===\ncommit {self.id}\nDate: {s}\n{self.message}\n"

    def safe_checkout(self, current_commit: Commit) -> bool:
        """Determines whether it is safe to make a checkout.

        Safe means that checking out of all the files in this commit would not
        make any files untracked in the current commit inaccessible.
        """
        for name in self.tracked:
            file = WORKING_DIR / name
            if file.exists() and name not in current_commit.tracked:
                return False
        return True

    def checkout(self, current_commit: Commit) -> None:
        """Puts all files of this commit the the working directory.

        Overwrites the versions of the files tracked by the current commit.

        Deletes all the files that are presented in the current commit, but
        not tracked by this commit.
        """
        for name, blob in self.tracked.items():
            file = WORKING_DIR / name
            file.write_bytes(blob.content)
        for name in current_commit.tracked:
            if name not in self.tracked:
                file = WORKING_DIR / name
                file.unlink()

    def split_point(self, other: Commit) -> Commit:
        """Finds split point of SELF and OTHER commits."""
        self_history = self.history2()
        other_history = other.history2()
        g = Graph()
        for commit_node in self_history:
            for parent_id in commit_node.parents:
                g.add(parent_id, commit_node.id)
        for commit_node in other_history:
            for parent_id in commit_node.parents:
                g.add(parent_id, commit_node.id)
        start = self_history[-1].id
        p = self.id
        q = other.id
        split_point_id = g.latest_common_ancestor(start, p, q)
        return Commit.load(split_point_id)

    @staticmethod
    def list_all() -> list[Commit]:
        """List all commits ever made in this repository."""
        commits = []
        for file in COMMIT_DIR.iterdir():
            commits.append(Commit.load(file.name))
        return commits
