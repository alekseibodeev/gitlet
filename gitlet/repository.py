from datetime import datetime
from gitlet.commit import Commit
from gitlet.branch import Branch
from gitlet.constants import (
    GITLET_DIR,
    BRANCH_DIR,
    COMMIT_DIR,
    BLOB_DIR,
    HEAD_FILE,
    INDEX_FILE,
)
from gitlet.error import RepositoryAlreadyExists


def write_head(name: str) -> None:
    """Sets HEAD pointer to the branch with the given name."""
    HEAD_FILE.write_text(name)


def init():
    """Creates a new Gitlet version-control system in the current directory.

    This system will automatically start one commit: a commit that contains
    no files and has the commit message "initial commit".

    The timestamp for this commit will be "00:00:00 UTC, Thursday, 1 January 1970".

    It will have a single branch: "master", which initially points to this
    initial commit, and "master" will be the current branch.

    If there is already a Gitlet version-control system in the current directory,
    it should abort with the following error message:
    - "A Gitlet version-control system already exists in the current directory."
    """
    # A Gitlet repository is expected to have the following inner structure:
    #
    # repository
    # └── .gitlet
    #     ├── blobs
    #     ├── branches
    #     ├── commits
    #     ├── HEAD
    #     └── INDEX
    #
    if GITLET_DIR.exists():
        raise RepositoryAlreadyExists()
    # Initialize inner directory structure
    GITLET_DIR.mkdir()
    BRANCH_DIR.mkdir()
    COMMIT_DIR.mkdir()
    BLOB_DIR.mkdir()
    HEAD_FILE.touch()
    INDEX_FILE.touch()
    # Create required objects
    initial_commit = Commit("initial commit", datetime(1970, 1, 1), [], {})
    master_branch = Branch("master", initial_commit.id)
    # Save whatever should be saved
    initial_commit.dump()
    master_branch.dump()
    write_head(master_branch.name)
