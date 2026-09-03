from __future__ import annotations

from typing import Callable, TypeVar


T = TypeVar("T")


def merge_sort(items: list[T], compare: Callable[[T, T], int]) -> list[T]:
    """sorted(), list.sort()를 쓰지 않는 안정 merge sort."""

    if len(items) <= 1:
        return items[:]

    mid = len(items) // 2
    left = merge_sort(items[:mid], compare)
    right = merge_sort(items[mid:], compare)
    return _merge(left, right, compare)


def _merge(left: list[T], right: list[T], compare: Callable[[T, T], int]) -> list[T]:
    result: list[T] = []
    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):
        if compare(left[left_index], right[right_index]) <= 0:
            result.append(left[left_index])
            left_index += 1
        else:
            result.append(right[right_index])
            right_index += 1

    while left_index < len(left):
        result.append(left[left_index])
        left_index += 1

    while right_index < len(right):
        result.append(right[right_index])
        right_index += 1

    return result

