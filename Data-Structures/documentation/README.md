# Data Structures — Lab

A from-scratch tour of five classic data structures in Python: a singly
linked list, a stack and queue, a binary search tree, a graph (adjacency
list), and a hash table with separate chaining. Each structure is
implemented using only the Python standard library, with its own internal
node/pointer or bucket layout rather than being a thin wrapper around a
built-in container.

## Folder layout

```
Data-Structures/
├── source/
│   ├── linked_list.py           # Singly linked list
│   ├── stack_queue.py           # Stack (LIFO) and Queue (FIFO)
│   ├── binary_search_tree.py    # Binary search tree
│   ├── graph.py                 # Graph (adjacency list) with BFS/DFS
│   └── hash_table.py            # Hash table with separate chaining
├── tests/
│   └── test_data_structures.py  # unittest suite for all five structures
└── documentation/
    └── README.md                # this file
```

## Concepts demonstrated

- **`linked_list.py`** — a `Node`-based singly linked list. Keeps both a
  head and tail pointer (so `append` is O(1), not O(n)) and a running size
  counter (so `__len__` is O(1)). Supports `append`, `prepend`, `delete`,
  `find`, `to_list`, iteration, and `len()`.

- **`stack_queue.py`** — a `Stack` (LIFO) and `Queue` (FIFO), each backed
  by its own private singly linked chain of nodes (not `list` or
  `collections.deque`). Both raise a dedicated `StructureEmptyError` on
  underflow (`pop`/`peek` on an empty stack, `dequeue`/`peek` on an empty
  queue) instead of letting an unrelated exception leak out.

- **`binary_search_tree.py`** — a classic (unbalanced) BST. `insert` and
  `search` walk the ordering invariant (left < node < right); `delete`
  handles all three removal cases (leaf, one child, two children — the
  two-children case splices in the in-order successor). Traversals
  (`in_order`, `pre_order`, `post_order`) are implemented as generators, so
  callers can iterate lazily without materializing a full list. Duplicate
  keys inserted twice are treated as a no-op (the tree behaves like a set
  of unique values).

- **`graph.py`** — an adjacency-list `Graph` (`dict[vertex] -> set[vertex]`),
  supporting both directed and undirected edges via `add_edge`. Provides
  `bfs` (queue-based, level-by-level), `dfs` (iterative, explicit-stack),
  and `dfs_recursive` (recursive form) — all three track a `visited` set,
  so a graph containing a cycle is traversed safely (every vertex is
  visited exactly once, no infinite loop).

- **`hash_table.py`** — a `HashTable` using **separate chaining**: an
  array of buckets, where each bucket holds a small linked chain of
  `(key, value)` entries. Collisions (distinct keys hashing to the same
  bucket) are resolved by walking that bucket's chain. The table doubles
  its capacity and rehashes all entries once the load factor exceeds
  `max_load_factor` (default `0.75`), keeping average-case operations
  close to O(1). Setting an already-present key overwrites its value
  in place rather than creating a duplicate entry.

## Time complexity summary

| Structure | Operation | Average case | Worst case | Notes |
|---|---|---|---|---|
| Linked List | `append` | O(1) | O(1) | tail pointer maintained |
| Linked List | `prepend` | O(1) | O(1) | |
| Linked List | `find` | O(n) | O(n) | linear scan |
| Linked List | `delete(value)` | O(n) | O(n) | must locate the node first |
| Linked List | `__len__` | O(1) | O(1) | running size counter |
| Stack | `push` | O(1) | O(1) | |
| Stack | `pop` | O(1) | O(1) | raises on empty stack |
| Stack | `peek` | O(1) | O(1) | raises on empty stack |
| Queue | `enqueue` | O(1) | O(1) | |
| Queue | `dequeue` | O(1) | O(1) | raises on empty queue |
| Queue | `peek` | O(1) | O(1) | raises on empty queue |
| Binary Search Tree | `insert` | O(log n) | O(n) | worst case on sorted/adversarial input (degenerates to a "linked list" tree) |
| Binary Search Tree | `search` | O(log n) | O(n) | same as above |
| Binary Search Tree | `delete` | O(log n) | O(n) | same as above |
| Binary Search Tree | traversal (in/pre/post-order) | O(n) | O(n) | visits every node once |
| Graph | `add_edge` | O(1) | O(1) | amortized set insertion |
| Graph | `bfs` / `dfs` | O(V + E) | O(V + E) | V = vertices, E = edges; each visited once |
| Hash Table | `set` | O(1) | O(n) | worst case: all keys collide into one bucket |
| Hash Table | `get` | O(1) | O(n) | same as above |
| Hash Table | `delete` | O(1) | O(n) | same as above |

Notes on the worst-case column:
- The BST here is **not self-balancing** (no AVL/red-black rotations), so
  inserting already-sorted data produces a degenerate, linked-list-shaped
  tree, pushing `insert`/`search`/`delete` to O(n).
- The hash table's worst case (O(n) per operation) occurs only when the
  hash function distributes all keys into the same bucket; with Python's
  built-in `hash()` and the table's automatic resizing/rehashing, this is
  not expected in normal use — the *average* case (amortized O(1)) is what
  the implementation is designed for.

## Running the code

Each module has a small runnable demo at the bottom, guarded by
`if __name__ == "__main__":`. From the `Data-Structures/` directory:

```bash
python source/linked_list.py
python source/stack_queue.py
python source/binary_search_tree.py
python source/graph.py
python source/hash_table.py
```

## Running the tests

From the `Data-Structures/` directory:

```bash
python -m unittest tests/test_data_structures.py -v
```

or, using discovery:

```bash
python -m unittest discover -s tests -v
```

The suite (32 tests) covers each structure's core operations plus at least
one edge case:

- **Linked List** — operating on an empty list (`find`, `delete`, `len`,
  `to_list` all behave correctly with no elements).
- **Stack / Queue** — underflow: `pop`/`peek` (stack) and
  `dequeue`/`peek` (queue) raise `StructureEmptyError` when empty.
- **Binary Search Tree** — duplicate-key insertion is a no-op (size and
  traversal output are unaffected), plus a fully empty-tree case.
- **Graph** — cycle-safe traversal: a 3-vertex cycle (`A -> B -> C -> A`)
  is traversed by `bfs`, `dfs`, and `dfs_recursive` without looping
  forever, visiting each vertex exactly once.
- **Hash Table** — duplicate-key `set` overwrites the existing value
  instead of duplicating the entry, and a forced single-bucket collision
  scenario confirms separate chaining correctly stores and retrieves
  multiple colliding keys independently.
