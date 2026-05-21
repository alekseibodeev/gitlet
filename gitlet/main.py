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
    except GitletException as e:
        print(e, file=sys.stderr)
        exit(1)
