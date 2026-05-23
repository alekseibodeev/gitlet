ID = r"(?P<id>[a-f0-9]{40})"
DATE = r"(?P<date>\w\w\w \w\w\w \d\d \d\d:\d\d:\d\d \d\d\d\d)"
MESSAGE = r"(?P<message>.+)"
LOG = rf"===\ncommit {ID}\nDate: {DATE}\n{MESSAGE}\n\n"
