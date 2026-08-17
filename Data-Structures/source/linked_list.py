"""
linked_list.py

A singly linked list implementation from scratch.

Concepts demonstrated:
- Node-based dynamic data structure (no built-in list/deque used internally).
- Pointer manipulation for insertion/deletion at both ends and arbitrary positions.
- Linear traversal for search, length, and conversion to a Python list.

Time complexity (see documentation/README.md for the full table):
- append/prepend: O(1) each (tail pointer is maintained).
- find/delete(by value): O(n).
- __len__: O(1) (a running size counter is maintained).
"""

from typing import Any, Iterator, List, Optional


class Node:
    """A single node in the linked list, holding a value and a pointer to the next node."""

    __slots__ = ("value", "next")

    def __init__(self, value: Any, next_node: Optional["Node"] = None) -> None:
        self.value = value
        self.next = next_node

    def __repr__(self) -> str:
        return f"Node({self.value!r})"


class LinkedList:
    """
    A singly linked list.

    Maintains both a head and tail pointer so that append() and prepend()
    run in O(1) time, and a size counter so that __len__() runs in O(1) time.
    """

    def __init__(self, iterable: Optional[Any] = None) -> None:
        self._head: Optional[Node] = None
        self._tail: Optional[Node] = None
        self._size: int = 0
        if iterable is not None:
            for value in iterable:
                self.append(value)

    # ------------------------------------------------------------------
    # Core mutation operations
    # ------------------------------------------------------------------
    def append(self, value: Any) -> None:
        """Insert a new value at the end of the list. O(1)."""
        node = Node(value)
        if self._head is None:
            self._head = node
            self._tail = node
        else:
            # self._tail is guaranteed not None here since head is not None.
            self._tail.next = node  # type: ignore[union-attr]
            self._tail = node
        self._size += 1

    def prepend(self, value: Any) -> None:
        """Insert a new value at the front of the list. O(1)."""
        node = Node(value, next_node=self._head)
        self._head = node
        if self._tail is None:
            self._tail = node
        self._size += 1

    def delete(self, value: Any) -> bool:
        """
        Delete the first node whose value equals `value`.

        Returns True if a node was removed, False if the value was not found
        (i.e. deleting from an empty list, or a missing value, is a no-op
        that reports failure rather than raising).
        """
        previous: Optional[Node] = None
        current = self._head
        while current is not None:
            if current.value == value:
                if previous is None:
                    self._head = current.next
                else:
                    previous.next = current.next
                if current is self._tail:
                    self._tail = previous
                self._size -= 1
                return True
            previous = current
            current = current.next
        return False

    def find(self, value: Any) -> Optional[Node]:
        """Return the first Node whose value equals `value`, or None if absent. O(n)."""
        current = self._head
        while current is not None:
            if current.value == value:
                return current
            current = current.next
        return None

    def __contains__(self, value: Any) -> bool:
        return self.find(value) is not None

    def to_list(self) -> List[Any]:
        """Return a plain Python list with the same elements, in order. O(n)."""
        result = []
        current = self._head
        while current is not None:
            result.append(current.value)
            current = current.next
        return result

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[Any]:
        current = self._head
        while current is not None:
            yield current.value
            current = current.next

    def __repr__(self) -> str:
        return f"LinkedList({self.to_list()!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LinkedList):
            return self.to_list() == other.to_list()
        if isinstance(other, list):
            return self.to_list() == other
        return NotImplemented


if __name__ == "__main__":
    ll = LinkedList([1, 2, 3])
    ll.append(4)
    ll.prepend(0)
    print(ll)  # LinkedList([0, 1, 2, 3, 4])
    print(len(ll))  # 5
    print(ll.find(3))  # Node(3)
    ll.delete(0)
    print(ll.to_list())  # [1, 2, 3, 4]
