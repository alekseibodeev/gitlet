class GitletException(Exception):
    pass


class RepositoryAlreadyExists(GitletException):
    def __init__(self):
        super().__init__(
            "A Gitlet version-control system already exists in the current directory."
        )


class FileExistsException(GitletException):
    def __init__(self):
        super().__init__("File does not exist.")


class NoChangesException(GitletException):
    def __init__(self):
        super().__init__("No changes added to the commit.")


class BlankMessageExcepiton(GitletException):
    def __init__(self):
        super().__init__("Please enter a commit message.")


class CommitExistsException(GitletException):
    def __init__(self):
        super().__init__("No commit with that id exists.")


class FileNotTrackedExcepiton(GitletException):
    def __init__(self):
        super().__init__("File does not exist in that commit.")


class NoReasonToRemoveException(GitletException):
    def __init__(self):
        super().__init__("No reason to remove the file.")


class BranchExistsException(GitletException):
    def __init__(self):
        super().__init__("A branch with that name already exists.")


class NoBranchExistsException(GitletException):
    def __init__(self):
        super().__init__("No such branch exists.")


class HeadCheckoutException(GitletException):
    def __init__(self):
        super().__init__("No need to checkout the current branch.")


class CheckoutUnsafeException(GitletException):
    def __init__(self):
        super().__init__(
            "There is an untracked file in the way; delete it, or add and commmit it first."
        )


class UncommitedChangexException(GitletException):
    def __init__(self):
        super().__init__("You have uncommited changes.")


class MergeItselfException(GitletException):
    def __init__(self):
        super().__init__("Cannot merge a branch with itself.")


class CurrentBranchRemoveException(GitletException):
    def __init__(self):
        super().__init__("Cannot remove the current branch.")
