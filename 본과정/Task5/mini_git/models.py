from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Commit:
    """Mini Git의 커밋 노드."""

    hash: str
    message: str
    author: str
    timestamp: str
    parents: list[str]

