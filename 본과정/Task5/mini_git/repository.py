from __future__ import annotations

from datetime import datetime

from .hashmap import HashMap
from .models import Commit
from .sorting import merge_sort


class MiniGit:
    """브랜치, 커밋 그래프, 검색 인덱스를 관리하는 핵심 클래스."""

    def __init__(self) -> None:
        self.initialized = False
        self.author = ""
        self.head_branch = ""
        self._counter = 0
        self._commits = HashMap()
        self._branches = HashMap()
        self._commit_order: list[str] = []
        self._keyword_index = HashMap()
        self._author_index = HashMap()

    def init(self, user_name: str) -> list[str]:
        if not user_name:
            return ["Invalid args"]

        self.__init__()
        self.initialized = True
        self.author = user_name
        self.head_branch = "main"
        self._branches.put("main", None)
        return [f"Initialized repository for {user_name}", "Current branch: main"]

    def branch(self, branch_name: str) -> list[str]:
        if not self._is_ready():
            return ["Repository not initialized"]
        if not branch_name:
            return ["Invalid args"]
        if self._branches.contains(branch_name):
            return [f"Branch already exists: {branch_name}"]

        self._branches.put(branch_name, self._current_head())
        return [f"Created branch: {branch_name}"]

    def switch(self, branch_name: str) -> list[str]:
        if not self._is_ready():
            return ["Repository not initialized"]
        if not self._branches.contains(branch_name):
            return [f"Unknown branch: {branch_name}"]

        self.head_branch = branch_name
        return [f"Switched to branch: {branch_name}"]

    def commit(self, message: str) -> list[str]:
        if not self._is_ready():
            return ["Repository not initialized"]
        if not message:
            return ["Invalid args"]

        parent = self._current_head()
        parents = [] if parent is None else [parent]
        commit_hash = self._next_hash()
        commit = Commit(
            hash=commit_hash,
            message=message,
            author=self.author,
            timestamp=datetime.now().isoformat(timespec="seconds"),
            parents=parents,
        )

        self._commits.put(commit.hash, commit)
        self._commit_order.append(commit.hash)
        self._branches.put(self.head_branch, commit.hash)
        self._add_to_indexes(commit)
        return [f"Committed {commit.hash}: {commit.message}"]

    def log(self, sort_by: str | None = None) -> list[str]:
        if not self._is_ready():
            return ["Repository not initialized"]

        commits = self._all_commits()
        if not commits:
            return ["No commits"]

        if sort_by == "date":
            commits = merge_sort(commits, _compare_by_date)
        elif sort_by == "author":
            commits = merge_sort(commits, _compare_by_author)
        elif sort_by is not None:
            return ["Invalid args"]

        return [_format_commit(commit) for commit in commits]

    def search_keyword(self, keyword: str) -> list[str]:
        if not self._is_ready():
            return ["Repository not initialized"]
        if not keyword:
            return ["Invalid args"]

        hashes = self._keyword_index.get(keyword.lower())
        return self._format_hashes(hashes)

    def search_author(self, author: str) -> list[str]:
        if not self._is_ready():
            return ["Repository not initialized"]
        if not author:
            return ["Invalid args"]

        hashes = self._author_index.get(author.lower())
        return self._format_hashes(hashes)

    def ancestors(self, commit_hash: str) -> list[str]:
        if not self._is_ready():
            return ["Repository not initialized"]
        if not self._commits.contains(commit_hash):
            return [f"Unknown commit: {commit_hash}"]

        result: list[str] = []
        stack: list[str] = []
        commit = self._commits.get(commit_hash)
        for parent in commit.parents:
            stack.append(parent)

        while stack:
            current_hash = stack.pop()
            if _contains(result, current_hash):
                continue
            result.append(current_hash)

            current_commit = self._commits.get(current_hash)
            if current_commit is not None:
                for parent in current_commit.parents:
                    stack.append(parent)

        if not result:
            return ["No ancestors"]
        return result

    def path(self, start: str, end: str) -> list[str]:
        if not self._is_ready():
            return ["Repository not initialized"]
        if not self._commits.contains(start):
            return [f"Unknown commit: {start}"]
        if not self._commits.contains(end):
            return [f"Unknown commit: {end}"]
        if start == end:
            return [start]

        found_paths = self._shortest_paths(start, end)
        if not found_paths:
            return ["No path"]

        ordered = merge_sort(found_paths, _compare_path_text)
        return ["->".join(ordered[0])]

    def _is_ready(self) -> bool:
        return self.initialized

    def _current_head(self) -> str | None:
        return self._branches.get(self.head_branch)

    def _next_hash(self) -> str:
        while True:
            self._counter += 1
            commit_hash = f"C{self._counter:06d}"
            if not self._commits.contains(commit_hash):
                return commit_hash

    def _add_to_indexes(self, commit: Commit) -> None:
        self._add_index_value(self._author_index, commit.author.lower(), commit.hash)
        for token in commit.message.split():
            normalized = token.lower()
            if normalized:
                self._add_index_value(self._keyword_index, normalized, commit.hash)

    def _add_index_value(self, index: HashMap, key: str, commit_hash: str) -> None:
        values = index.get(key)
        if values is None:
            values = []
            index.put(key, values)
        if not _contains(values, commit_hash):
            values.append(commit_hash)

    def _all_commits(self) -> list[Commit]:
        result: list[Commit] = []
        for commit_hash in self._commit_order:
            commit = self._commits.get(commit_hash)
            if commit is not None:
                result.append(commit)
        return result

    def _format_hashes(self, hashes: list[str] | None) -> list[str]:
        if not hashes:
            return ["No commits"]

        commits: list[Commit] = []
        for commit_hash in hashes:
            commit = self._commits.get(commit_hash)
            if commit is not None:
                commits.append(commit)

        if not commits:
            return ["No commits"]
        return [_format_commit(commit) for commit in commits]

    def _shortest_paths(self, start: str, end: str) -> list[list[str]]:
        queue: list[list[str]] = [[start]]
        visited_depths: list[tuple[str, int]] = [(start, 0)]
        found_paths: list[list[str]] = []
        found_depth: int | None = None
        queue_index = 0

        while queue_index < len(queue):
            path = queue[queue_index]
            queue_index += 1
            current = path[-1]
            depth = len(path) - 1

            if found_depth is not None and depth > found_depth:
                break
            if current == end:
                found_depth = depth
                found_paths.append(path)
                continue

            for neighbor in self._neighbors(current):
                if _contains(path, neighbor):
                    continue
                next_depth = depth + 1
                previous_depth = _visited_depth(visited_depths, neighbor)
                if previous_depth is not None and previous_depth < next_depth:
                    continue
                if previous_depth is None:
                    visited_depths.append((neighbor, next_depth))
                queue.append(path + [neighbor])

        return found_paths

    def _neighbors(self, commit_hash: str) -> list[str]:
        result: list[str] = []
        commit = self._commits.get(commit_hash)
        if commit is not None:
            for parent in commit.parents:
                if not _contains(result, parent):
                    result.append(parent)

        for other_hash in self._commit_order:
            other = self._commits.get(other_hash)
            if other is not None and _contains(other.parents, commit_hash):
                if not _contains(result, other.hash):
                    result.append(other.hash)

        return merge_sort(result, _compare_text)


def _format_commit(commit: Commit) -> str:
    parents = ",".join(commit.parents) if commit.parents else "-"
    return f"{commit.hash} | {commit.author} | {commit.timestamp} | parents={parents} | {commit.message}"


def _compare_text(left: str, right: str) -> int:
    if left < right:
        return -1
    if left > right:
        return 1
    return 0


def _compare_path_text(left: list[str], right: list[str]) -> int:
    return _compare_text("->".join(left), "->".join(right))


def _compare_by_date(left: Commit, right: Commit) -> int:
    date_result = _compare_text(left.timestamp, right.timestamp)
    if date_result != 0:
        return date_result
    return _compare_text(left.hash, right.hash)


def _compare_by_author(left: Commit, right: Commit) -> int:
    author_result = _compare_text(left.author.lower(), right.author.lower())
    if author_result != 0:
        return author_result
    return _compare_text(left.hash, right.hash)


def _contains(items: list, value: object) -> bool:
    for item in items:
        if item == value:
            return True
    return False


def _visited_depth(items: list[tuple[str, int]], commit_hash: str) -> int | None:
    for item_hash, depth in items:
        if item_hash == commit_hash:
            return depth
    return None

