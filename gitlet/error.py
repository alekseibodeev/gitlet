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
