from __future__ import annotations

import shlex

from .repository import MiniGit


def run_command(repo: MiniGit, line: str) -> list[str] | None:
    try:
        parts = shlex.split(line)
    except ValueError:
        return ["Invalid args"]

    if not parts:
        return []

    command = parts[0].upper()
    if command in ("EXIT", "QUIT"):
        return None

    if command == "INIT":
        if len(parts) != 2:
            return ["Invalid args"]
        return repo.init(parts[1])

    if command == "BRANCH":
        if len(parts) != 2:
            return ["Invalid args"]
        return repo.branch(parts[1])

    if command == "SWITCH":
        if len(parts) != 2:
            return ["Invalid args"]
        return repo.switch(parts[1])

    if command == "COMMIT":
        if len(parts) != 2:
            return ["Invalid args"]
        return repo.commit(parts[1])

    if command == "LOG":
        return _run_log(repo, parts)

    if command == "PATH":
        if len(parts) != 3:
            return ["Invalid args"]
        return repo.path(parts[1], parts[2])

    if command == "ANCESTORS":
        if len(parts) != 2:
            return ["Invalid args"]
        return repo.ancestors(parts[1])

    if command == "SEARCH":
        return _run_search(repo, parts)

    return [f"Unknown command: {parts[0]}"]


def repl() -> int:
    repo = MiniGit()

    while True:
        try:
            line = input("mini-git> ")
        except EOFError:
            print()
            return 0
        except KeyboardInterrupt:
            print()
            return 0

        output = run_command(repo, line)
        if output is None:
            return 0
        for row in output:
            print(row)


def main() -> int:
    return repl()


def _run_log(repo: MiniGit, parts: list[str]) -> list[str]:
    if len(parts) == 1:
        return repo.log()
    if len(parts) == 2 and parts[1].startswith("--sort-by="):
        sort_by = parts[1].split("=", 1)[1]
        return repo.log(sort_by=sort_by)
    return ["Invalid args"]


def _run_search(repo: MiniGit, parts: list[str]) -> list[str]:
    if len(parts) != 2:
        return ["Invalid args"]

    query = parts[1]
    if query.startswith("--author="):
        author = query.split("=", 1)[1]
        return repo.search_author(author)

    return repo.search_keyword(query)

