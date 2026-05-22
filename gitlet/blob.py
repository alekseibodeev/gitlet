from hashlib import sha1
from typing import Any

from gitlet.constants import BLOB_DIR, WORKING_DIR
from gitlet.error import FileExistsException


class Blob:
    """Represents a Gitlet blob object.

    Every blob has unique identifier, and all blobs with the same identifier
    will have the same content. The blobs are thus content addressable.

    Attributes:
    id -- unique identifier produced by SHA-1 hash function
    content -- the actual content of this blob
    """

    def __init__(self, id: str, content: bytes | None = None) -> None:
        self.id = id
        self._content = content

    @property
    def content(self):
        # Loads blob's content lazily on demand
        if not self._content:
            file = BLOB_DIR / self.id
            self._content = file.read_bytes()
        return self._content

    def __eq__(self, other):
        if not isinstance(other, Blob):
            return NotImplemented
        return self.id == other.id

    def __getstate__(self):
        return {"id": self.id}

    def __setstate__(self, state: dict[str, Any]):
        self.id = state["id"]
        self._content = None

    def dump(self) -> None:
        file = BLOB_DIR / self.id
        file.write_bytes(self.content)

    @staticmethod
    def from_file(name: str) -> Blob:
        """Creates a new blob from the given file."""
        file = WORKING_DIR / name
        if not file.exists():
            raise FileExistsException()
        content = file.read_bytes()
        blob_id = sha1(content).hexdigest()
        return Blob(blob_id, content)
