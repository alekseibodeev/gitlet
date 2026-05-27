import pickle

from gitlet.constants import BRANCH_DIR
from gitlet.error import NoBranchExistsException


class Branch:
    """Represents a Gitlet branch object.

    Attributes:
    name -- a name of this branch
    head -- the last commit made on this branch
    """

    def __init__(self, name: str, commit: str) -> None:
        self.name = name
        self.head = commit

    def serialize(self) -> bytes:
        return pickle.dumps(self)

    def dump(self) -> None:
        file = BRANCH_DIR / self.name
        file.write_bytes(self.serialize())

    @staticmethod
    def load(name: str) -> Branch:
        file = BRANCH_DIR / name
        if not file.exists():
            raise NoBranchExistsException()
        content = file.read_bytes()
        return pickle.loads(content)

    def exists(self) -> bool:
        file = BRANCH_DIR / self.name
        return file.exists()

    @staticmethod
    def list() -> list[str]:
        """Lists all existing branches in sorted order."""
        branches: list[str] = []
        for b in BRANCH_DIR.iterdir():
            branches.append(b.name)
        branches.sort()
        return branches
