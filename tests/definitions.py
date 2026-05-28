import re

ID = r"(?P<id>[a-f0-9]{40})"
DATE = r"(?P<date>\w\w\w \w\w\w \d\d \d\d:\d\d:\d\d \d\d\d\d)"
MESSAGE = r"(?P<message>.+)"
LOG = rf"===\ncommit {ID}\nDate: {DATE}\n{MESSAGE}\n\n"
BRANCHES = r"=== Branches ===\n(?P<branches>(.+\n)*)\n"
STAGED = r"=== Staged Files ===\n(?P<staged>(.+\n)*)\n"
REMOVED = r"=== Removed Files ===\n(?P<removed>(.+\n)*)\n"
MODIFICATIONS = (
    r"=== Modifications Not Staged For Commit ===\n(?P<modifications>(.+\n)*)\n"
)
UNTRACKED = r"=== Untracked Files ===\n(?P<untracked>(.+\n)*)\n"
STATUS = rf"{BRANCHES}{STAGED}{REMOVED}{MODIFICATIONS}{UNTRACKED}"


def parse_status_message(message: str) -> list[list[str]]:
    match = re.fullmatch(STATUS, message)
    assert match
    branches = match.group("branches").strip().split()
    staged = match.group("staged").strip().split()
    removed = match.group("removed").strip().split()
    modifications = []
    for mod in match.group("modifications").strip().split("\n"):
        modifications.append(mod.split(" ")[0])
    untracked = match.group("untracked").strip().split()
    return [branches, staged, removed, modifications, untracked]
