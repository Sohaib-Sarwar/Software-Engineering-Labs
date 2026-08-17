"""
searching_algorithms.py

Standalone implementations of two classic searching algorithms:
    - linear_search
    - binary_search

Both functions search for a target value inside a sequence and return
the index of the first matching element, or -1 if the target is not
found.
"""

from typing import Sequence, TypeVar

T = TypeVar("T")


def linear_search(items: Sequence[T], target: T) -> int:
    """
    Search ``items`` for ``target`` by checking every element in order.

    Works on any sequence regardless of ordering, since it makes no
    assumption about how the elements are arranged.

    :param items: Sequence of elements to search through.
    :param target: The value to search for.
    :return: The index of the first occurrence of ``target`` in
        ``items``, or -1 if it is not present.
    """
    for index, value in enumerate(items):
        if value == target:
            return index
    return -1


def binary_search(items: Sequence[T], target: T) -> int:
    """
    Search ``items`` for ``target`` using binary search.

    IMPORTANT: This function assumes ``items`` is already sorted in
    ascending order. Calling it on unsorted data gives undefined
    (generally incorrect) results.

    Repeatedly narrows the search range by comparing ``target`` to the
    middle element of the current range and discarding the half of the
    range that cannot contain it.

    :param items: A sequence sorted in ascending order.
    :param target: The value to search for.
    :return: The index of ``target`` in ``items``, or -1 if it is not
        present.
    """
    low = 0
    high = len(items) - 1

    while low <= high:
        mid = (low + high) // 2
        mid_value = items[mid]

        if mid_value == target:
            return mid
        elif mid_value < target:
            low = mid + 1
        else:
            high = mid - 1

    return -1


if __name__ == "__main__":
    data = [1, 3, 4, 6, 8, 9, 11, 15, 20]
    print("Data:", data)
    print("linear_search for 11:", linear_search(data, 11))
    print("binary_search for 11:", binary_search(data, 11))
    print("linear_search for 99:", linear_search(data, 99))
    print("binary_search for 99:", binary_search(data, 99))
