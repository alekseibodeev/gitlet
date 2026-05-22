from datetime import datetime
from gitlet.blob import Blob
from gitlet.commit import Commit
from gitlet.branch import Branch
from gitlet.constants import (
    GITLET_DIR,
    BRANCH_DIR,
    COMMIT_DIR,
    BLOB_DIR,
    HEAD_FILE,
    INDEX_FILE,
    WORKING_DIR,
)
from gitlet.error import (
    BlankMessageExcepiton,
    FileNotTrackedExcepiton,
    NoChangesException,
    RepositoryAlreadyExists,
)
from gitlet import index


def write_head(name: str) -> None:
    """Sets HEAD pointer to the branch with the given name."""
    HEAD_FILE.write_text(name)


def read_head() -> str:
    """Retrieves HEAD pointer from persistence storage."""
    return HEAD_FILE.read_text()


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
    index.dump()
    write_head(master_branch.name)


def add(name: str) -> None:
    """Adds a copy of the file as it currently exists to the staging area.

    Staging an already staged file overwrites the previous entry in the staging
    area with the new contents.

    If the current working version of the file is identical to the version in
    the current commit, do not stage it to be added, and remove it from the staging
    area if it is already there.

    The file will no longer be staged for removal if it was at the time of the
    command.

    If the file does not exist exit and print error message:
    - "File does not exist."

    Arguments:
    name -- the name of the file to stage
    """
    blob = Blob.from_file(name)
    branch = Branch.load(read_head())
    commit = Commit.load(branch.head)
    index.load()
    if name in commit.tracked and commit.tracked[name] == blob:
        if name in index.added:
            del index.added[name]
    else:
        index.added[name] = blob
    if name in index.removed:
        index.removed.remove(name)
    blob.dump()
    index.dump()


def commit(message: str) -> None:
    """Creates a new commit.

    Saves a snapshot of tracked files in the current commit and staging area so
    they can be restored at a later time.

    A commit will save and start tracking any files that were staged for addition,
    but weren't tracked by its parent.

    Files, tracked in the current commit may be untracked as a result being
    staged for removal.

    The staging area should be cleared after commit.

    The commit command never adds, changes or removes files in the working directory.

    Any changes made to files after staging for addition or removal are ignored
    by the commid command.

    After the commid command, the new commit becomes the current commit, and
    the head pointer now points to it.

    If no files have been staged, abort with error message:
    - "No changes added to the commit."

    If the given message is blank (or empty), exit with the following error:
    - "Please enter a commit message"

    Arguments:
    message -- a message associated with this commit
    """
    index.load()
    if index.empty():
        raise NoChangesException()
    if not message:
        raise BlankMessageExcepiton()
    current_branch = Branch.load(read_head())
    current_commit = Commit.load(current_branch.head)
    new_commit = current_commit.commit(message)
    current_branch.head = new_commit.id
    current_branch.dump()
    new_commit.dump()
    index.clear()
    index.dump()


def checkout(name: str, commit_id: str | None = None, is_branch: bool = False) -> None:
    """Checkout file or branch to the working directory.

    There are three possible use cases for this command:

    1. Takes the version of the file as it exists in the head commit and puts it
    in the working directory, overwriting the version of the file that's already
    there if there is one.

    2. Takes the version of the file as it exists in the commit with the given id,
    and puts it in the working directory, overwriting the version of the file that's
    already there.

    3. Takes all files in the commit at the head of the given branch, and puts
    them in the working directory. Also, at the end of this command, the given
    branch will now be considered the curren branch (HEAD). Any files that are
    tracked in the current branch, but are not presented in the checked-out branch
    are deleted. The staging area is cleared.

    If the file does not exist in the previous commit, abort with error:
    - "File does not exist in that commit."

    If no commit with the given id exists, print:
    - "No commit with that id exists."

    If no branch with that name exists, exit with message:
    - "No such branch exists."

    If that branch is the current branch, print:
    - "No need to checkout the current branch."

    If a file is untracked in the current branch and would be overwritten by
    the checkout, abort and print error:
    - "There is an untracked file in the way; delete it, or add and commmit it first."

    Arguments:
    name -- the name of a file or a branch
    commit_id -- the id of the given commit (can be less than 40 characters)
    is_branch -- determines whether the name should be considered as a file or a branch
    """
    current_branch = Branch.load(read_head())
    current_commit = Commit.load(current_branch.head)
    if not is_branch:
        if not commit_id:
            given_commit = current_commit
        else:
            given_commit = Commit.load(commit_id)
        if name not in given_commit.tracked:
            raise FileNotTrackedExcepiton()
        file = WORKING_DIR / name
        blob = given_commit.tracked[name]
        file.write_bytes(blob.content)
    else:
        pass  # TODO: implement case (3) branch checkout
