"""
binary_search_tree.py

An unbalanced binary search tree (BST) implementation.

Concepts demonstrated:
- Ordered binary tree invariant: for any node, all values in the left
  subtree are smaller and all values in the right subtree are larger.
- Recursive insert/search/delete, including the classic "two children"
  deletion case (replace with the in-order successor).
- Generator-based traversals (in-order, pre-order, post-order) that yield
  values lazily instead of building an intermediate list.

Time complexity note: because this BST does not self-balance, average-case
times below assume roughly random insertion order; a sorted/adversarial
insertion order degenerates the tree into a linked list (O(n) worst case
for insert/search/delete).
"""

from typing import Any, Iterator, Optional


class BSTNode:
    __slots__ = ("value", "left", "right")

    def __init__(self, value: Any) -> None:
        self.value = value
        self.left: Optional["BSTNode"] = None
        self.right: Optional["BSTNode"] = None


class BinarySearchTree:
    """A binary search tree supporting insert, search, delete, and traversals."""

    def __init__(self) -> None:
        self._root: Optional[BSTNode] = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._root is None

    # ------------------------------------------------------------------
    # Insert
    # ------------------------------------------------------------------
    def insert(self, value: Any) -> None:
        """
        Insert a value into the tree. Duplicate values are ignored (a BST
        with duplicates would require a tie-breaking rule; this
        implementation treats the structure as a set of unique keys).
        """
        if self._root is None:
            self._root = BSTNode(value)
            self._size += 1
            return
        self._insert_recursive(self._root, value)

    def _insert_recursive(self, node: BSTNode, value: Any) -> None:
        if value == node.value:
            return  # duplicate: no-op
        if value < node.value:
            if node.left is None:
                node.left = BSTNode(value)
                self._size += 1
            else:
                self._insert_recursive(node.left, value)
        else:
            if node.right is None:
                node.right = BSTNode(value)
                self._size += 1
            else:
                self._insert_recursive(node.right, value)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------
    def search(self, value: Any) -> bool:
        """Return True if `value` exists in the tree, else False."""
        return self._search_recursive(self._root, value)

    def _search_recursive(self, node: Optional[BSTNode], value: Any) -> bool:
        if node is None:
            return False
        if value == node.value:
            return True
        if value < node.value:
            return self._search_recursive(node.left, value)
        return self._search_recursive(node.right, value)

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------
    def delete(self, value: Any) -> bool:
        """
        Delete `value` from the tree if present.

        Returns True if a node was removed, False if the value was not found.
        """
        self._root, removed = self._delete_recursive(self._root, value)
        if removed:
            self._size -= 1
        return removed

    def _delete_recursive(
        self, node: Optional[BSTNode], value: Any
    ) -> "tuple[Optional[BSTNode], bool]":
        if node is None:
            return None, False

        if value < node.value:
            node.left, removed = self._delete_recursive(node.left, value)
            return node, removed
        if value > node.value:
            node.right, removed = self._delete_recursive(node.right, value)
            return node, removed

        # value == node.value: this is the node to remove.
        if node.left is None and node.right is None:
            return None, True
        if node.left is None:
            return node.right, True
        if node.right is None:
            return node.left, True

        # Two children: replace this node's value with its in-order
        # successor (smallest value in the right subtree), then delete
        # that successor from the right subtree.
        successor = node.right
        while successor.left is not None:
            successor = successor.left
        node.value = successor.value
        node.right, _ = self._delete_recursive(node.right, successor.value)
        return node, True

    # ------------------------------------------------------------------
    # Traversals (generators)
    # ------------------------------------------------------------------
    def in_order(self) -> Iterator[Any]:
        """Yield values in ascending sorted order."""
        yield from self._in_order(self._root)

    def _in_order(self, node: Optional[BSTNode]) -> Iterator[Any]:
        if node is not None:
            yield from self._in_order(node.left)
            yield node.value
            yield from self._in_order(node.right)

    def pre_order(self) -> Iterator[Any]:
        """Yield values as: node, left subtree, right subtree."""
        yield from self._pre_order(self._root)

    def _pre_order(self, node: Optional[BSTNode]) -> Iterator[Any]:
        if node is not None:
            yield node.value
            yield from self._pre_order(node.left)
            yield from self._pre_order(node.right)

    def post_order(self) -> Iterator[Any]:
        """Yield values as: left subtree, right subtree, node."""
        yield from self._post_order(self._root)

    def _post_order(self, node: Optional[BSTNode]) -> Iterator[Any]:
        if node is not None:
            yield from self._post_order(node.left)
            yield from self._post_order(node.right)
            yield node.value

    def __iter__(self) -> Iterator[Any]:
        """Default iteration is in-order (sorted) traversal."""
        return self.in_order()


if __name__ == "__main__":
    bst = BinarySearchTree()
    for v in [5, 3, 8, 1, 4, 7, 9]:
        bst.insert(v)
    print(list(bst.in_order()))    # [1, 3, 4, 5, 7, 8, 9]
    print(list(bst.pre_order()))   # [5, 3, 1, 4, 8, 7, 9]
    print(list(bst.post_order()))  # [1, 4, 3, 7, 9, 8, 5]
    print(bst.search(7))           # True
    bst.delete(5)
    print(list(bst.in_order()))    # [1, 3, 4, 7, 8, 9]
