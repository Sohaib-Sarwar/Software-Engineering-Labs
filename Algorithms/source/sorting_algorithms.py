"""
sorting_algorithms.py

Standalone implementations of four classic sorting algorithms:
    - bubble_sort
    - insertion_sort
    - merge_sort
    - quick_sort

Each function takes an iterable of comparable elements and returns a
*new* sorted list in ascending order. None of these functions mutate
the input list that was passed in.
"""

from typing import List, Sequence, TypeVar

T = TypeVar("T")


def bubble_sort(items: Sequence[T]) -> List[T]:
    """
    Sort ``items`` using the bubble sort algorithm.

    Repeatedly steps through the list, compares adjacent elements, and
    swaps them if they are in the wrong order. The pass repeats until
    no swaps are needed. Includes the standard optimization that stops
    early once the list is already sorted.

    :param items: Sequence of comparable elements.
    :return: A new list containing the elements of ``items`` in
        ascending order.
    """
    result = list(items)
    n = len(result)

    for i in range(n):
        swapped = False
        # After each pass, the largest remaining element "bubbles" to
        # the end, so we don't need to re-check the last i elements.
        for j in range(0, n - i - 1):
            if result[j] > result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]
                swapped = True
        if not swapped:
            break

    return result


def insertion_sort(items: Sequence[T]) -> List[T]:
    """
    Sort ``items`` using the insertion sort algorithm.

    Builds the sorted list one element at a time by taking each
    element from the input and inserting it into its correct position
    among the already-sorted elements to its left.

    :param items: Sequence of comparable elements.
    :return: A new list containing the elements of ``items`` in
        ascending order.
    """
    result = list(items)

    for i in range(1, len(result)):
        key = result[i]
        j = i - 1
        while j >= 0 and result[j] > key:
            result[j + 1] = result[j]
            j -= 1
        result[j + 1] = key

    return result


def merge_sort(items: Sequence[T]) -> List[T]:
    """
    Sort ``items`` using the merge sort algorithm.

    A classic divide-and-conquer algorithm: recursively splits the
    list in half, sorts each half, and merges the two sorted halves
    back together.

    :param items: Sequence of comparable elements.
    :return: A new list containing the elements of ``items`` in
        ascending order.
    """
    data = list(items)

    if len(data) <= 1:
        return data

    mid = len(data) // 2
    left = merge_sort(data[:mid])
    right = merge_sort(data[mid:])

    return _merge(left, right)


def _merge(left: List[T], right: List[T]) -> List[T]:
    """Merge two already-sorted lists into a single sorted list."""
    merged: List[T] = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    merged.extend(left[i:])
    merged.extend(right[j:])

    return merged


def quick_sort(items: Sequence[T]) -> List[T]:
    """
    Sort ``items`` using the quicksort algorithm.

    A divide-and-conquer algorithm that selects a pivot element,
    partitions the remaining elements into those less than, equal to,
    and greater than the pivot, and recursively sorts the partitions.
    This implementation uses the middle element as the pivot, which
    avoids worst-case O(n^2) behavior on already-sorted input.

    :param items: Sequence of comparable elements.
    :return: A new list containing the elements of ``items`` in
        ascending order.
    """
    data = list(items)

    if len(data) <= 1:
        return data

    pivot = data[len(data) // 2]
    less = [x for x in data if x < pivot]
    equal = [x for x in data if x == pivot]
    greater = [x for x in data if x > pivot]

    return quick_sort(less) + equal + quick_sort(greater)


if __name__ == "__main__":
    sample = [5, 2, 9, 1, 5, 6, 3, 8, 7, 4]
    print("Original:      ", sample)
    print("bubble_sort:   ", bubble_sort(sample))
    print("insertion_sort:", insertion_sort(sample))
    print("merge_sort:    ", merge_sort(sample))
    print("quick_sort:    ", quick_sort(sample))
    print("Original unchanged:", sample)
