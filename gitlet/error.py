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
