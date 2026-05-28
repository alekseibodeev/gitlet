from datetime import datetime

from gitlet import index
from gitlet.blob import Blob
from gitlet.branch import Branch
from gitlet.commit import Commit
from gitlet.constants import (
    BLOB_DIR,
    BRANCH_DIR,
    COMMIT_DIR,
    GITLET_DIR,
    HEAD_FILE,
    INDEX_FILE,
    WORKING_DIR,
)
from gitlet.error import (
    BlankMessageExcepiton,
    BranchExistsException,
    CheckoutUnsafeException,
    CurrentBranchRemoveException,
    FileNotTrackedExcepiton,
    HeadCheckoutException,
    MergeItselfException,
    NoChangesException,
    NoReasonToRemoveException,
    RepositoryAlreadyExists,
    UncommitedChangexException,
)


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
    if not message.strip():
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
        given_branch = Branch.load(name)
        if current_branch.name == given_branch.name:
            raise HeadCheckoutException()
        given_commit = Commit.load(given_branch.head)
        if not given_commit.safe_checkout(current_commit):
            raise CheckoutUnsafeException()
        given_commit.checkout(current_commit)
        write_head(given_branch.name)
        # If the staging area (INDEX) is not loaded it starts empty,
        # so it's safe to just dump it in order to perform clean up
        index.dump()


def log() -> None:
    """Displays commit history.

    Starting at the current head commit, output information about each commit
    backwards along the commit tree until the initial commit, following the first
    parent commit links, ingnoring any second parents found in merge commits.

    Example of exact history format:

    ===
    commit a0da1ea5a15ab613bf9961fd86f010cf74c7ee48
    Date: Thu Nov 09 20:00:05 2017
    A commit message.

    ===
    commit 3e8bf1d794ca2e9ef8a4007275acf3751c7170ff
    Date: Thu Nov 09 17:01:33 2017
    Another commit message.

    ===
    commit e881c9575d180a215d1a636545b8fd9abfb1d2bb
    Date: Thu Jan 01 00:00:00 1970
    initial commit
    """
    current_branch = Branch.load(read_head())
    current_commit = Commit.load(current_branch.head)
    for commit_node in current_commit.history():
        print(commit_node)


def global_log() -> None:
    """Displays information about all commits ever made."""
    for commit_node in Commit.list_all():
        print(commit_node)


def remove(name: str) -> None:
    """Stages file for removal.

    Unstage the file if it is currently staged for addition.

    If the file is tracked in the current commit, stage it for removal and remove
    the file from working directory if the user has not already done so.

    If the file is neither staged nor tracked by the head commit, print error:
    - "No reason to remove the file."

    Arguments:
    name -- a name of the file to remove
    """
    current_branch = Branch.load(read_head())
    current_commit = Commit.load(current_branch.head)
    index.load()
    if name in index.added:
        del index.added[name]
    elif name in current_commit.tracked:
        index.removed.add(name)
        file = WORKING_DIR / name
        if file.exists():
            file.unlink()
    else:
        raise NoReasonToRemoveException()
    index.dump()


def branch(name: str) -> None:
    """Creates a new branch with the given name.

    Newly created branch points at the current head commit.

    This command does not immediately switch to the newly created branch.

    If a branch with the given name already exists, print the error message:
    - "A branch with that name already exists."

    Attributes:
    name -- a new of the new branch
    """
    current_branch = Branch.load(read_head())
    current_commit = Commit.load(current_branch.head)
    new_branch = Branch(name, current_commit.id)
    if new_branch.exists():
        raise BranchExistsException()
    new_branch.dump()


def remove_branch(name: str) -> None:
    """Deletes the pointer associated with the branch with the given name.

    If a branch with the given name does not exists, exit with error message:
    - "No such branch exists."

    If you try to remove the branch you're currently on, abort and prints:
    - "Cannot remove the current branch."
    """
    current_branch = Branch.load(read_head())
    given_branch = Branch.load(name)
    if current_branch.name == given_branch.name:
        raise CurrentBranchRemoveException()
    given_branch.remove()


def get_conflict_message(current_content: bytes, given_content: bytes) -> bytes:
    return b"<<<<<<< HEAD\n%s=======\n%s>>>>>>>\n" % (current_content, given_content)


def merge(name: str) -> None:
    """Merges files from the given branch to the current branch.

    If the split point is the same commit as the given branch, then the merge is
    complete and the operation ends with the message:
    - "Given branch is an ancestor of the current branch."

    If the split point it the current branch's head, then the effect is to check
    out the given branch, and print the message:
    - "Current branch fast-forwarded."

    Otherwise program continues with the following steps:

    1. Any files that have been modified in the given branch since the split point,
    but not modified the current branch should be changed to their versions in
    the given branch

    2. Any files that have been modified in the current branch, but not in the
    given branch since the split point should stay as they are

    3. Any files that have been modified in both the current and the given branches
    in the same way are left unchanged by the merge.

    4. Any files that were not presented at the split point and are presented
    only in the current branch should remain as they are

    5. Any files that were not presented at the split point and are presented
    only in the given branch should be checked out

    6. Any files presented at the split point, unmodified at the current branch
    and absent in the given branch should be removed

    7. Any files presented at the split point, unmodified at the given branch and
    absent in the current branch should remain absent

    8. Any files modified in a different ways in the current and the given branches
    are in conflict.

    The content of the files in conflict should be replaced with:
    <<<<<<< HEAD
    content of the file in current branch
    =======
    content of the file in given branch
    >>>>>>>

    If the merge encoutered the conflict, prints the message:
    - "Encountered a merge conflict."

    Merge should be automatically commited with the following message:
    - "Merged <given branch> into <current branch>."

    Merge commits have two parents.

    If staging area is not empty, abort and print error message:
    - "You have uncommited changes."

    If a branch with the given name does not exist, print error message:
    - "No such branch exists."

    If attemption to merge a branch with itself, should print error:
    - "Cannot merge a branch with itself."

    If a file is untracked in the current branch and would be overwritten by
    the merge, abort and print error:
    - "There is an untracked file in the way; delete it, or add and commmit it first."

    Arguments:
    name -- a name of the branch to merge
    """
    index.load()
    if not index.empty():
        raise UncommitedChangexException()
    current_branch = Branch.load(read_head())
    given_branch = Branch.load(name)
    if current_branch.name == given_branch.name:
        raise MergeItselfException()
    current_commit = Commit.load(current_branch.head)
    given_commit = Commit.load(given_branch.head)
    if not given_commit.safe_checkout(current_commit):
        raise CheckoutUnsafeException()
    split_point = current_commit.split_point(given_commit)
    if split_point == given_commit:
        print("Given branch is an ancestor of the current branch.")
    elif split_point == current_commit:
        given_commit.checkout(current_commit)
        current_branch.head = given_commit.id
        current_branch.dump()
        print("Current branch fast-forwarded.")
    else:
        conflict = False
        for name, given_blob in given_commit.tracked.items():
            current_blob = current_commit.tracked.get(name, Blob.stub())
            split_blob = split_point.tracked.get(name, Blob.stub())
            if given_blob != split_blob:
                if current_blob == split_blob:
                    index.added[name] = given_blob
                else:
                    conflict = True
                    content = get_conflict_message(
                        current_blob.content, given_blob.content
                    )
                    blob = Blob.from_content(content)
                    blob.dump()
                    index.added[name] = blob
        for name, current_blob in current_commit.tracked.items():
            given_blob = given_commit.tracked.get(name, Blob.stub())
            split_blob = split_point.tracked.get(name, Blob.stub())
            if given_blob == Blob.stub() and split_blob != Blob.stub():
                if current_blob == split_blob:
                    index.removed.add(name)
                else:
                    conflict = True
                    content = get_conflict_message(
                        current_blob.content, given_blob.content
                    )
                    blob = Blob.from_content(content)
                    blob.dump()
                    index.added[name] = blob
        message = f"Merged {given_branch.name} into {current_branch.name}."
        new_commit = current_commit.commit(message)
        new_commit.parents.append(given_commit.id)
        new_commit.checkout(current_commit)
        current_branch.head = new_commit.id
        new_commit.dump()
        current_branch.dump()
        if conflict:
            print("Encountered a merge conflict.")


def get_modified(current_commit: Commit) -> list[str]:
    """Returns a sorted list of files modified in the working directory."""
    files: list[str] = []
    for name, current_blob in current_commit.tracked.items():
        file = WORKING_DIR / name
        if file.exists():
            blob = Blob.from_file(name)
            if current_blob != blob and (
                name not in index.added or index.added[name] != blob
            ):
                files.append(name)
    files.sort()
    return files


def get_deleted(current_commit: Commit) -> list[str]:
    """Returns a sorted list of files deleted from the working directory."""
    files = set()
    for name in current_commit.tracked:
        file = WORKING_DIR / name
        if not file.exists() and name not in index.removed:
            files.add(name)
    for name in index.added:
        file = WORKING_DIR / name
        if not file.exists():
            files.add(name)
    return sorted(files)


def get_untracked(current_commit: Commit) -> list[str]:
    """Returns a sorted list of untracked files."""
    files: list[str] = []
    for file in WORKING_DIR.iterdir():
        if file.is_file():
            name = str(file)
            if name not in current_commit.tracked and name not in index.added:
                files.append(name)
    files.sort()
    return files


def status() -> None:
    """Prints out the current state of the working directory.

    Displays what branches currently exist, and marks the current branch with a *.
    Also displays what files have been staged for addition or removal, modified
    or untracked.

    Modified files are:
    - Tracked in the current commit, changed in the working directory, but not
      staged
    - Staged for addition, but with different contents than in the working directory
    - Staged for addition, but deleted in the working directory
    - Not staged for removal, but tracked in the current commit and deleted from
      the working directory

    Untracked files are files presented in the working directory, but neither
    staged nor tracked in the head commit.

    There is an empty line after each section.

    Example format:
    === Branches ===
    *master
    other

    === Staged Files ===
    hello.txt
    world.txt

    === Removed Files ===
    mars.txt

    === Modifications Not Staged For Commit ===
    goodbye.txt (modified)
    junk.txt (deleted)

    === Untracked Files ===
    lorem.txt

    """
    index.load()
    current_branch = Branch.load(read_head())
    current_commit = Commit.load(current_branch.head)
    branches = Branch.list()
    print("=== Branches ===")
    for name in branches:
        if name == current_branch.name:
            print("*" + name)
        else:
            print(name)
    print()
    staged = sorted(index.added)
    print("=== Staged Files ===")
    for name in staged:
        print(name)
    print()
    removed = sorted(index.removed)
    print("=== Removed Files ===")
    for name in removed:
        print(name)
    print()
    modified = get_modified(current_commit)
    deleted = get_deleted(current_commit)
    print("=== Modifications Not Staged For Commit ===")
    i = 0
    j = 0
    while i < len(modified) and j < len(deleted):
        if modified[i] < deleted[i]:
            print(modified[i], "(modified)")
            i += 1
        else:
            print(deleted[i], "(deleted)")
            j += 1
    while i < len(modified):
        print(modified[i], "(modified)")
        i += 1
    while j < len(deleted):
        print(deleted[j], "(deleted)")
        j += 1
    print()
    untracked = get_untracked(current_commit)
    print("=== Untracked Files ===")
    for name in untracked:
        print(name)
    print()
