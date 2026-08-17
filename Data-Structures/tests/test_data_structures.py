"""
test_data_structures.py

unittest suite covering the core operations of every data structure in
source/, plus at least one edge case per structure:
    - LinkedList:         empty-list operations
    - Stack / Queue:      underflow on an empty structure
    - BinarySearchTree:   duplicate-key insertion
    - Graph:               cycle-safe BFS/DFS traversal
    - HashTable:          duplicate-key overwrite (and collision handling)

Run from the `Data-Structures` directory with:
    python -m unittest tests/test_data_structures.py -v
or simply:
    python -m unittest discover -s tests -v
"""

import os
import sys
import unittest

# Allow running this file directly (e.g. `python tests/test_data_structures.py`)
# by putting the subject folder's root on sys.path so `source.*` resolves,
# regardless of the caller's current working directory.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from source.linked_list import LinkedList
from source.stack_queue import Stack, Queue, StructureEmptyError
from source.binary_search_tree import BinarySearchTree
from source.graph import Graph
from source.hash_table import HashTable, KeyNotFoundError


class TestLinkedList(unittest.TestCase):
    def test_append_and_to_list(self):
        ll = LinkedList()
        ll.append(1)
        ll.append(2)
        ll.append(3)
        self.assertEqual(ll.to_list(), [1, 2, 3])
        self.assertEqual(len(ll), 3)

    def test_prepend(self):
        ll = LinkedList([2, 3])
        ll.prepend(1)
        self.assertEqual(ll.to_list(), [1, 2, 3])
        self.assertEqual(len(ll), 3)

    def test_find(self):
        ll = LinkedList([10, 20, 30])
        node = ll.find(20)
        self.assertIsNotNone(node)
        self.assertEqual(node.value, 20)
        self.assertIsNone(ll.find(999))

    def test_delete_middle_and_ends(self):
        ll = LinkedList([1, 2, 3, 4])
        self.assertTrue(ll.delete(1))   # delete head
        self.assertEqual(ll.to_list(), [2, 3, 4])
        self.assertTrue(ll.delete(4))   # delete tail
        self.assertEqual(ll.to_list(), [2, 3])
        self.assertTrue(ll.delete(3))   # delete remaining tail
        self.assertEqual(ll.to_list(), [2])

    def test_delete_missing_value_returns_false(self):
        ll = LinkedList([1, 2, 3])
        self.assertFalse(ll.delete(999))
        self.assertEqual(ll.to_list(), [1, 2, 3])

    def test_edge_case_empty_list(self):
        """Edge case: operations on an empty LinkedList must not error."""
        ll = LinkedList()
        self.assertEqual(len(ll), 0)
        self.assertEqual(ll.to_list(), [])
        self.assertIsNone(ll.find(1))
        self.assertFalse(ll.delete(1))  # deleting from empty list is a no-op
        # After emptying a previously non-empty list, tail bookkeeping must
        # also be consistent -- appending again should still work.
        ll.append(42)
        self.assertEqual(ll.to_list(), [42])

    def test_delete_all_then_state_is_clean(self):
        ll = LinkedList([1])
        self.assertTrue(ll.delete(1))
        self.assertEqual(len(ll), 0)
        self.assertEqual(ll.to_list(), [])
        ll.prepend(5)
        self.assertEqual(ll.to_list(), [5])


class TestStack(unittest.TestCase):
    def test_push_pop_peek_order(self):
        s = Stack()
        s.push(1)
        s.push(2)
        s.push(3)
        self.assertEqual(s.peek(), 3)
        self.assertEqual(s.pop(), 3)
        self.assertEqual(s.pop(), 2)
        self.assertEqual(len(s), 1)
        self.assertEqual(s.pop(), 1)
        self.assertEqual(len(s), 0)

    def test_edge_case_pop_underflow_raises(self):
        """Edge case: popping/peeking an empty stack raises StructureEmptyError."""
        s = Stack()
        self.assertTrue(s.is_empty())
        with self.assertRaises(StructureEmptyError):
            s.pop()
        with self.assertRaises(StructureEmptyError):
            s.peek()


class TestQueue(unittest.TestCase):
    def test_enqueue_dequeue_peek_order(self):
        q = Queue()
        q.enqueue("a")
        q.enqueue("b")
        q.enqueue("c")
        self.assertEqual(q.peek(), "a")
        self.assertEqual(q.dequeue(), "a")
        self.assertEqual(q.dequeue(), "b")
        self.assertEqual(len(q), 1)
        self.assertEqual(q.dequeue(), "c")
        self.assertEqual(len(q), 0)

    def test_edge_case_dequeue_underflow_raises(self):
        """Edge case: dequeuing/peeking an empty queue raises StructureEmptyError."""
        q = Queue()
        self.assertTrue(q.is_empty())
        with self.assertRaises(StructureEmptyError):
            q.dequeue()
        with self.assertRaises(StructureEmptyError):
            q.peek()

    def test_queue_reusable_after_draining(self):
        """Rear pointer must reset correctly after the queue empties out."""
        q = Queue()
        q.enqueue(1)
        q.dequeue()
        q.enqueue(2)
        q.enqueue(3)
        self.assertEqual(q.dequeue(), 2)
        self.assertEqual(q.dequeue(), 3)


class TestBinarySearchTree(unittest.TestCase):
    def test_insert_and_search(self):
        bst = BinarySearchTree()
        for v in [5, 3, 8, 1, 4, 7, 9]:
            bst.insert(v)
        self.assertTrue(bst.search(7))
        self.assertFalse(bst.search(100))
        self.assertEqual(len(bst), 7)

    def test_traversals(self):
        bst = BinarySearchTree()
        for v in [5, 3, 8, 1, 4, 7, 9]:
            bst.insert(v)
        self.assertEqual(list(bst.in_order()), [1, 3, 4, 5, 7, 8, 9])
        self.assertEqual(list(bst.pre_order()), [5, 3, 1, 4, 8, 7, 9])
        self.assertEqual(list(bst.post_order()), [1, 4, 3, 7, 9, 8, 5])

    def test_delete_leaf_one_child_two_children(self):
        bst = BinarySearchTree()
        for v in [5, 3, 8, 1, 4, 7, 9]:
            bst.insert(v)

        # Leaf node.
        self.assertTrue(bst.delete(1))
        self.assertFalse(bst.search(1))

        # Node with a single child (4 now has no children, 3 has only child 4).
        self.assertTrue(bst.delete(3))
        self.assertFalse(bst.search(3))
        self.assertTrue(bst.search(4))  # child was reattached

        # Node with two children (root, 5).
        self.assertTrue(bst.delete(5))
        self.assertFalse(bst.search(5))
        self.assertEqual(list(bst.in_order()), [4, 7, 8, 9])

    def test_delete_missing_value_returns_false(self):
        bst = BinarySearchTree()
        bst.insert(10)
        self.assertFalse(bst.delete(999))

    def test_edge_case_duplicate_keys_are_ignored(self):
        """Edge case: inserting a duplicate key must not create a second node."""
        bst = BinarySearchTree()
        bst.insert(5)
        bst.insert(5)
        bst.insert(5)
        self.assertEqual(len(bst), 1)
        self.assertEqual(list(bst.in_order()), [5])

    def test_edge_case_empty_tree(self):
        bst = BinarySearchTree()
        self.assertTrue(bst.is_empty())
        self.assertEqual(len(bst), 0)
        self.assertFalse(bst.search(1))
        self.assertFalse(bst.delete(1))
        self.assertEqual(list(bst.in_order()), [])
        self.assertEqual(list(bst.pre_order()), [])
        self.assertEqual(list(bst.post_order()), [])


class TestGraph(unittest.TestCase):
    def test_add_edge_undirected_both_directions(self):
        g = Graph()
        g.add_edge("A", "B")
        self.assertIn("B", g.neighbors("A"))
        self.assertIn("A", g.neighbors("B"))

    def test_add_edge_directed_one_direction(self):
        g = Graph(directed=True)
        g.add_edge("A", "B")
        self.assertIn("B", g.neighbors("A"))
        self.assertNotIn("A", g.neighbors("B"))

    def test_bfs_order(self):
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("A", "C")
        g.add_edge("B", "D")
        g.add_edge("C", "D")
        order = g.bfs("A")
        self.assertEqual(order[0], "A")
        self.assertEqual(set(order), {"A", "B", "C", "D"})
        # D is reachable only via B or C, so it must come after both.
        self.assertLess(order.index("A"), order.index("D"))

    def test_dfs_visits_all_reachable_nodes(self):
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("A", "C")
        g.add_edge("B", "D")
        g.add_edge("C", "D")
        order = g.dfs("A")
        self.assertEqual(order[0], "A")
        self.assertEqual(set(order), {"A", "B", "C", "D"})

    def test_edge_case_cycle_safe_traversal(self):
        """Edge case: a graph containing a cycle must not loop forever, and
        every reachable vertex must be visited exactly once."""
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("C", "A")  # closes a cycle A -> B -> C -> A

        bfs_order = g.bfs("A")
        dfs_order = g.dfs("A")
        dfs_recursive_order = g.dfs_recursive("A")

        for order in (bfs_order, dfs_order, dfs_recursive_order):
            self.assertEqual(len(order), 3)
            self.assertEqual(set(order), {"A", "B", "C"})
            self.assertEqual(len(order), len(set(order)))  # no repeats

    def test_start_vertex_not_in_graph_raises(self):
        g = Graph()
        g.add_edge("A", "B")
        with self.assertRaises(KeyError):
            g.bfs("Z")
        with self.assertRaises(KeyError):
            g.dfs("Z")


class TestHashTable(unittest.TestCase):
    def test_set_get_basic(self):
        table = HashTable()
        table.set("apple", 1)
        table.set("banana", 2)
        self.assertEqual(table.get("apple"), 1)
        self.assertEqual(table.get("banana"), 2)
        self.assertEqual(len(table), 2)

    def test_delete(self):
        table = HashTable()
        table.set("apple", 1)
        table.delete("apple")
        self.assertNotIn("apple", table)
        self.assertEqual(len(table), 0)

    def test_delete_missing_key_raises(self):
        table = HashTable()
        with self.assertRaises(KeyNotFoundError):
            table.delete("missing")

    def test_get_missing_key_raises_without_default(self):
        table = HashTable()
        with self.assertRaises(KeyNotFoundError):
            table.get("missing")

    def test_get_missing_key_returns_default_when_given(self):
        table = HashTable()
        self.assertEqual(table.get("missing", "fallback"), "fallback")

    def test_resize_preserves_all_entries(self):
        """Force several resizes and confirm every key/value survives rehashing."""
        table = HashTable(initial_capacity=2, max_load_factor=0.75)
        expected = {}
        for i in range(50):
            key = f"key{i}"
            table.set(key, i)
            expected[key] = i
        for key, value in expected.items():
            self.assertEqual(table.get(key), value)
        self.assertEqual(len(table), 50)

    def test_edge_case_duplicate_key_overwrites_value(self):
        """Edge case: setting the same key twice must overwrite, not duplicate."""
        table = HashTable()
        table.set("apple", 1)
        table.set("apple", 999)
        self.assertEqual(table.get("apple"), 999)
        self.assertEqual(len(table), 1)  # still only one entry
        self.assertEqual(list(table.keys()).count("apple"), 1)

    def test_edge_case_collision_handled_via_chaining(self):
        """Two distinct keys forced into the same bucket must both be
        retrievable independently (separate chaining in action)."""
        table = HashTable(initial_capacity=1)  # every key maps to bucket 0
        table.set("a", 1)
        table.set("b", 2)
        table.set("c", 3)
        self.assertEqual(table.get("a"), 1)
        self.assertEqual(table.get("b"), 2)
        self.assertEqual(table.get("c"), 3)
        table.delete("b")
        self.assertEqual(table.get("a"), 1)
        self.assertEqual(table.get("c"), 3)
        with self.assertRaises(KeyNotFoundError):
            table.get("b")


if __name__ == "__main__":
    unittest.main(verbosity=2)
