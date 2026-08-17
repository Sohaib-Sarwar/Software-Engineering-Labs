"""
stack_queue.py

Stack (LIFO) and Queue (FIFO) implementations built from scratch on top of a
private singly linked list of internal nodes. Neither class wraps Python's
built-in list or collections.deque for its storage -- both maintain their own
node/pointer structure directly.

Concepts demonstrated:
- LIFO vs FIFO ordering semantics.
- Node-based storage with O(1) push/pop (stack) and O(1) enqueue/dequeue
  (queue, via a maintained tail pointer).
- Defensive underflow handling via a dedicated exception type.
"""

from typing import Any, Optional


class StructureEmptyError(Exception):
    """Raised when an operation requires at least one element but the structure is empty."""


class _StackNode:
    __slots__ = ("value", "below")

    def __init__(self, value: Any, below: Optional["_StackNode"] = None) -> None:
        self.value = value
        self.below = below


class Stack:
    """
    A LIFO stack implemented with an internal singly linked structure.

    The most recently pushed element sits on "top" and is the first one
    popped or peeked.
    """

    def __init__(self) -> None:
        self._top: Optional[_StackNode] = None
        self._size = 0

    def push(self, value: Any) -> None:
        """Push a value onto the top of the stack. O(1)."""
        self._top = _StackNode(value, below=self._top)
        self._size += 1

    def pop(self) -> Any:
        """
        Remove and return the value on top of the stack.

        Raises StructureEmptyError if the stack is empty.
        """
        if self._top is None:
            raise StructureEmptyError("pop from an empty Stack")
        node = self._top
        self._top = node.below
        self._size -= 1
        return node.value

    def peek(self) -> Any:
        """
        Return (without removing) the value on top of the stack.

        Raises StructureEmptyError if the stack is empty.
        """
        if self._top is None:
            raise StructureEmptyError("peek at an empty Stack")
        return self._top.value

    def is_empty(self) -> bool:
        return self._top is None

    def __len__(self) -> int:
        return self._size

    def __repr__(self) -> str:
        values = []
        node = self._top
        while node is not None:
            values.append(node.value)
            node = node.below
        return f"Stack(top->{values})"


class _QueueNode:
    __slots__ = ("value", "next")

    def __init__(self, value: Any, next_node: Optional["_QueueNode"] = None) -> None:
        self.value = value
        self.next = next_node


class Queue:
    """
    A FIFO queue implemented with an internal singly linked structure.

    Maintains both a front and a rear pointer so that enqueue() and
    dequeue() both run in O(1) time.
    """

    def __init__(self) -> None:
        self._front: Optional[_QueueNode] = None
        self._rear: Optional[_QueueNode] = None
        self._size = 0

    def enqueue(self, value: Any) -> None:
        """Add a value to the rear of the queue. O(1)."""
        node = _QueueNode(value)
        if self._rear is None:
            self._front = node
            self._rear = node
        else:
            self._rear.next = node
            self._rear = node
        self._size += 1

    def dequeue(self) -> Any:
        """
        Remove and return the value at the front of the queue.

        Raises StructureEmptyError if the queue is empty.
        """
        if self._front is None:
            raise StructureEmptyError("dequeue from an empty Queue")
        node = self._front
        self._front = node.next
        if self._front is None:
            self._rear = None
        self._size -= 1
        return node.value

    def peek(self) -> Any:
        """
        Return (without removing) the value at the front of the queue.

        Raises StructureEmptyError if the queue is empty.
        """
        if self._front is None:
            raise StructureEmptyError("peek at an empty Queue")
        return self._front.value

    def is_empty(self) -> bool:
        return self._front is None

    def __len__(self) -> int:
        return self._size

    def __repr__(self) -> str:
        values = []
        node = self._front
        while node is not None:
            values.append(node.value)
            node = node.next
        return f"Queue(front->{values}<-rear)"


if __name__ == "__main__":
    s = Stack()
    s.push(1)
    s.push(2)
    s.push(3)
    print(s.pop())  # 3
    print(s.peek())  # 2

    q = Queue()
    q.enqueue("a")
    q.enqueue("b")
    q.enqueue("c")
    print(q.dequeue())  # a
    print(q.peek())  # b
