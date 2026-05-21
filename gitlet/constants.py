from pathlib import Path

WORKING_DIR = Path(".")
GITLET_DIR = WORKING_DIR / ".gitlet"
BRANCH_DIR = GITLET_DIR / "branches"
COMMIT_DIR = GITLET_DIR / "commits"
BLOB_DIR = GITLET_DIR / "blobs"
HEAD_FILE = GITLET_DIR / "HEAD"
INDEX_FILE = GITLET_DIR / "INDEX"

__all__ = [
    "WORKING_DIR",
    "GITLET_DIR",
    "BRANCH_DIR",
    "COMMIT_DIR",
    "BLOB_DIR",
    "HEAD_FILE",
    "INDEX_FILE",
]
