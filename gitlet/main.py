import sys

from gitlet import repository
from gitlet.error import GitletException


def main(args: list[str]) -> None:
    """Drive for Gitlet, a subset of the Git version-control system.

    Usage: gitlet <command> <operand1> <operand2> ...

    Arguments:
    args -- a command line arguments passed to the program
    """
    command = args[1]
    try:
        if command == "init":
            repository.init()
        elif command == "add":
            repository.add(args[2])
        elif command == "commit":
            repository.commit(args[2])
        elif command == "checkout":
            if len(args) == 4:
                repository.checkout(args[3])
            elif len(args) == 5:
                repository.checkout(args[4], args[2])
            elif len(args) == 3:
                repository.checkout(args[2], is_branch=True)
        elif command == "log":
            repository.log()
    except GitletException as e:
        print(e, file=sys.stderr)
        exit(1)
