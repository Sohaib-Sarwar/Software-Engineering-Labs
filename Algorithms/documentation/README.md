# Algorithms

A reference implementation of common sorting, searching, and recursion
algorithms in Python, together with a unittest suite that validates
each one.

## Folder structure

```
Algorithms/
├── source/
│   ├── sorting_algorithms.py     bubble sort, insertion sort, merge sort, quicksort
│   ├── searching_algorithms.py   linear search, binary search
│   └── recursion_examples.py     factorial, memoized fibonacci, N-Queens backtracking
├── tests/
│   └── test_algorithms.py        unittest suite covering all of the above
└── documentation/
    └── README.md                 this file
```

## Concepts demonstrated

### Sorting (`source/sorting_algorithms.py`)

- **Bubble sort** — repeatedly walks the list swapping adjacent
  out-of-order pairs, letting the largest unsorted element "bubble" to
  the end each pass. Includes an early-exit flag so an already-sorted
  list finishes in a single pass.
- **Insertion sort** — builds the sorted result one element at a time,
  inserting each new element into its correct position among the
  already-sorted elements to its left. Efficient on small or
  nearly-sorted inputs.
- **Merge sort** — a divide-and-conquer algorithm that recursively
  splits the list in half, sorts each half, and merges the two sorted
  halves back together. Guarantees O(n log n) regardless of input
  order, at the cost of extra memory.
- **Quicksort** — a divide-and-conquer algorithm that picks a pivot,
  partitions the data into elements less than, equal to, and greater
  than the pivot, and recursively sorts the partitions. This
  implementation picks the *middle* element as the pivot, which avoids
  the classic worst case on already-sorted input.

Every sorting function returns a **new** list; none of them mutate the
list passed in.

### Searching (`source/searching_algorithms.py`)

- **Linear search** — checks every element in order until it finds the
  target (or exhausts the sequence). Works on unsorted data.
- **Binary search** — repeatedly halves the search range by comparing
  the target to the middle element. **Requires the input to already be
  sorted in ascending order**; calling it on unsorted data produces
  undefined (generally incorrect) results. This assumption is called
  out explicitly in the function's docstring.

### Recursion (`source/recursion_examples.py`)

- **Factorial** — the textbook example of simple linear recursion:
  `n! = n * (n-1)!`, with `0! = 1! = 1` as the base case.
- **Fibonacci (memoized)** — naive recursive Fibonacci recomputes the
  same sub-problems exponentially many times. This implementation
  caches each computed value (in a shared module-level dict by
  default, or an isolated dict passed in by the caller) so every
  distinct sub-problem is solved exactly once, bringing the running
  time down to O(n).
- **N-Queens (backtracking)** — places queens one row at a time,
  tracking which columns and diagonals are already occupied. Whenever
  a row has no legal column left, the algorithm backtracks to the
  previous row and tries a different column. `solve_n_queens(n)`
  returns *all* distinct solutions for an `n`x`n` board (as an empty
  list when no solution exists, e.g. for `n = 2` or `n = 3`).

## Running the code

Each module can be run directly to see a short demonstration:

```bash
python source/sorting_algorithms.py
python source/searching_algorithms.py
python source/recursion_examples.py
```

## Running the tests

From the `Algorithms/` folder:

```bash
python -m unittest tests/test_algorithms.py -v
```

or, using test discovery:

```bash
python -m unittest discover -s tests -v
```

The test suite verifies:

- Every sorting algorithm against Python's built-in `sorted()` across
  several fixed (seeded) random lists, plus edge cases: empty list,
  single-element list, already-sorted list, reverse-sorted list, a
  list with duplicates, and a check that the input list is never
  mutated.
- `linear_search` and `binary_search` against known indices, including
  an empty-list edge case and a "not found" case.
- `factorial`, `fibonacci`, and `solve_n_queens`, including edge cases
  such as `n = 0`, negative-input errors, and boards with no solution
  (`solve_n_queens(2)` and `solve_n_queens(3)` both return `[]`).

## Complexity reference

All bounds below are in terms of `n`, the size of the input (list
length for sorting/searching, the numeric argument for factorial and
fibonacci, or the board size for N-Queens).

| Algorithm | Best | Average | Worst | Space |
|---|---|---|---|---|
| Bubble sort | O(n) | O(n²) | O(n²) | O(1) extra (in-place); O(n) for the returned copy |
| Insertion sort | O(n) | O(n²) | O(n²) | O(1) extra (in-place); O(n) for the returned copy |
| Merge sort | O(n log n) | O(n log n) | O(n log n) | O(n) |
| Quicksort | O(n log n) | O(n log n) | O(n²) | O(log n) average call stack; O(n) worst-case call stack (plus O(n) here for the partition lists this implementation builds) |
| Linear search | O(1) | O(n) | O(n) | O(1) |
| Binary search | O(1) | O(log n) | O(log n) | O(1) iterative |
| Factorial (recursive) | O(n) | O(n) | O(n) | O(n) call stack |
| Fibonacci (memoized) | O(n) | O(n) | O(n) | O(n) (cache + call stack) |
| N-Queens (backtracking) | O(n) (trivially, n ≤ 3 with early failure) | O(n!) roughly, pruned heavily by constraint checks | O(n!) | O(n) for the current placement / recursion depth, plus O(k·n) to store all `k` returned solutions |

**Note on bubble sort / insertion sort space:** the algorithms
themselves rearrange elements using only a constant amount of extra
scratch space (a temporary variable for swaps), so their *auxiliary*
space complexity is O(1). The O(n) figure only reflects the fact that
these functions copy the input into a new list before sorting it, per
this lab's requirement to return a new list rather than mutate the
original.

**Note on N-Queens:** there is no simple closed-form for the exact
number of ways the search tree gets pruned, so "O(n!)" is a common
upper-bound shorthand for the unconstrained brute-force search space;
the column/diagonal tracking in this implementation prunes the vast
majority of that space in practice.

### Why quicksort's worst case differs from its average case

Quicksort's O(n log n) average case comes from the pivot splitting the
list into two roughly balanced halves at each recursive step, so the
recursion depth is O(log n) and each of the O(log n) "levels" of
recursion does O(n) total work partitioning elements — giving O(n log
n) overall. The O(n²) worst case happens when the chosen pivot is
consistently one of the most extreme values in the current sublist
(the smallest or largest element), so instead of splitting the data
roughly in half, the pivot splits it into a partition of size 0 (or 1)
and a partition of size n-1. That turns the recursion into n nested
levels instead of log n, with O(n) work at each level, giving O(n) *
O(n) = O(n²). Naive implementations that always pick the first or last
element as the pivot hit this worst case on already-sorted or
reverse-sorted input; this lab's implementation instead picks the
*middle* element, which avoids that specific pathological case but
does not eliminate the theoretical worst case entirely — an adversary
who knows the pivot rule can still construct input that forces
maximally unbalanced partitions.
