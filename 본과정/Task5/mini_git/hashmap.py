from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Entry:
    key: str
    value: Any
    next: Entry | None = None


class HashMap:
    """체이닝 방식으로 구현한 간단한 해시맵."""

    def __init__(self, capacity: int = 8) -> None:
        self._capacity = max(2, capacity)
        self._buckets: list[Entry | None] = [None] * self._capacity
        self._size = 0

    def size(self) -> int:
        return self._size

    def _hash(self, key: str) -> int:
        value = 0
        for ch in key:
            value = (value * 31 + ord(ch)) & 0x7FFFFFFF
        return value

    def _index(self, key: str) -> int:
        return self._hash(key) % self._capacity

    def _resize(self) -> None:
        old_buckets = self._buckets
        self._capacity *= 2
        self._buckets = [None] * self._capacity
        old_size = self._size
        self._size = 0

        for bucket in old_buckets:
            current = bucket
            while current is not None:
                self.put(current.key, current.value)
                current = current.next

        self._size = old_size

    def put(self, key: str, value: Any) -> None:
        if (self._size + 1) / self._capacity > 0.75:
            self._resize()

        index = self._index(key)
        current = self._buckets[index]
        while current is not None:
            if current.key == key:
                current.value = value
                return
            current = current.next

        self._buckets[index] = Entry(key=key, value=value, next=self._buckets[index])
        self._size += 1

    def get(self, key: str) -> Any | None:
        current = self._buckets[self._index(key)]
        while current is not None:
            if current.key == key:
                return current.value
            current = current.next
        return None

    def contains(self, key: str) -> bool:
        current = self._buckets[self._index(key)]
        while current is not None:
            if current.key == key:
                return True
            current = current.next
        return False

    def keys(self) -> list[str]:
        result: list[str] = []
        for bucket in self._buckets:
            current = bucket
            while current is not None:
                result.append(current.key)
                current = current.next
        return result

