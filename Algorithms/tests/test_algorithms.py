"""
test_algorithms.py

Unit tests for the sorting, searching, and recursion modules found in
../source. Run with:

    python -m unittest tests/test_algorithms.py -v

from the Algorithms folder, or simply:

    python -m unittest discover -s tests -v
"""

import os
import random
import sys
import unittest

# Make ../source importable regardless of the current working directory.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_SOURCE_DIR = os.path.join(os.path.dirname(_THIS_DIR), "source")
if _SOURCE_DIR not in sys.path:
    sys.path.insert(0, _SOURCE_DIR)

from sorting_algorithms import bubble_sort, insertion_sort, merge_sort, quick_sort
from searching_algorithms import linear_search, binary_search
from recursion_examples import factorial, fibonacci, solve_n_queens


# ---------------------------------------------------------------------------
# Fixed (seeded) random input lists, generated once so every test run uses
# the exact same "random-but-fixed" data.
# ---------------------------------------------------------------------------
def _make_fixed_random_lists():
    rng = random.Random(42)
    lists = []
    for _ in range(5):
        size = rng.randint(0, 50)
        lists.append([rng.randint(-100, 100) for _ in range(size)])
    return lists


FIXED_RANDOM_LISTS = _make_fixed_random_lists()

SORT_FUNCTIONS = {
    "bubble_sort": bubble_sort,
    "insertion_sort": insertion_sort,
    "merge_sort": merge_sort,
    "quick_sort": quick_sort,
}


class TestSortingAlgorithms(unittest.TestCase):
    """Verify each sorting algorithm against Python's built-in sorted()."""

    def test_against_builtin_sorted_on_fixed_random_lists(self):
        for name, sort_fn in SORT_FUNCTIONS.items():
            for i, data in enumerate(FIXED_RANDOM_LISTS):
                with self.subTest(algorithm=name, list_index=i):
                    expected = sorted(data)
                    actual = sort_fn(data)
                    self.assertEqual(actual, expected)

    def test_empty_list(self):
        for name, sort_fn in SORT_FUNCTIONS.items():
            with self.subTest(algorithm=name):
                self.assertEqual(sort_fn([]), [])

    def test_single_element_list(self):
        for name, sort_fn in SORT_FUNCTIONS.items():
            with self.subTest(algorithm=name):
                self.assertEqual(sort_fn([42]), [42])

    def test_already_sorted_list(self):
        data = [1, 2, 3, 4, 5]
        for name, sort_fn in SORT_FUNCTIONS.items():
            with self.subTest(algorithm=name):
                self.assertEqual(sort_fn(data), [1, 2, 3, 4, 5])

    def test_reverse_sorted_list(self):
        data = [5, 4, 3, 2, 1]
        for name, sort_fn in SORT_FUNCTIONS.items():
            with self.subTest(algorithm=name):
                self.assertEqual(sort_fn(data), [1, 2, 3, 4, 5])

    def test_list_with_duplicates(self):
        data = [3, 1, 2, 3, 1, 2, 3, 0]
        expected = sorted(data)
        for name, sort_fn in SORT_FUNCTIONS.items():
            with self.subTest(algorithm=name):
                self.assertEqual(sort_fn(data), expected)

    def test_does_not_mutate_input(self):
        original = [5, 3, 4, 1, 2]
        snapshot = original.copy()
        for name, sort_fn in SORT_FUNCTIONS.items():
            with self.subTest(algorithm=name):
                sort_fn(original)
                self.assertEqual(original, snapshot)


class TestSearchingAlgorithms(unittest.TestCase):
    """Tests for linear_search and binary_search, including edge cases."""

    def setUp(self):
        self.sorted_data = [1, 3, 4, 6, 8, 9, 11, 15, 20]

    # -- linear_search --------------------------------------------------
    def test_linear_search_found(self):
        self.assertEqual(linear_search(self.sorted_data, 11), 6)

    def test_linear_search_not_found(self):
        self.assertEqual(linear_search(self.sorted_data, 99), -1)

    def test_linear_search_empty_list(self):
        self.assertEqual(linear_search([], 5), -1)

    def test_linear_search_unsorted_data(self):
        unsorted = [5, 3, 8, 1, 9]
        self.assertEqual(linear_search(unsorted, 8), 2)

    # -- binary_search ----------------------------------------------------
    def test_binary_search_found(self):
        self.assertEqual(binary_search(self.sorted_data, 11), 6)

    def test_binary_search_first_element(self):
        self.assertEqual(binary_search(self.sorted_data, 1), 0)

    def test_binary_search_last_element(self):
        last_index = len(self.sorted_data) - 1
        self.assertEqual(binary_search(self.sorted_data, 20), last_index)

    def test_binary_search_not_found(self):
        self.assertEqual(binary_search(self.sorted_data, 99), -1)

    def test_binary_search_empty_list(self):
        self.assertEqual(binary_search([], 5), -1)

    def test_binary_search_single_element_found(self):
        self.assertEqual(binary_search([7], 7), 0)

    def test_binary_search_single_element_not_found(self):
        self.assertEqual(binary_search([7], 3), -1)


class TestRecursionExamples(unittest.TestCase):
    """Tests for factorial, fibonacci, and solve_n_queens."""

    # -- factorial --------------------------------------------------------
    def test_factorial_zero(self):
        self.assertEqual(factorial(0), 1)

    def test_factorial_one(self):
        self.assertEqual(factorial(1), 1)

    def test_factorial_positive(self):
        self.assertEqual(factorial(5), 120)
        self.assertEqual(factorial(10), 3628800)

    def test_factorial_negative_raises(self):
        with self.assertRaises(ValueError):
            factorial(-1)

    # -- fibonacci ----------------------------------------------------------
    def test_fibonacci_base_cases(self):
        self.assertEqual(fibonacci(0), 0)
        self.assertEqual(fibonacci(1), 1)

    def test_fibonacci_known_values(self):
        expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
        for n, value in enumerate(expected):
            with self.subTest(n=n):
                self.assertEqual(fibonacci(n), value)

    def test_fibonacci_negative_raises(self):
        with self.assertRaises(ValueError):
            fibonacci(-5)

    def test_fibonacci_uses_isolated_cache(self):
        # Passing a fresh cache dict should not depend on prior module-level
        # cache state, and should still produce the correct result.
        isolated_cache = {0: 0, 1: 1}
        self.assertEqual(fibonacci(15, cache=isolated_cache), 610)

    # -- solve_n_queens ----------------------------------------------------
    def test_n_queens_zero_board(self):
        # A 0x0 board has exactly one (trivial, empty) solution.
        self.assertEqual(solve_n_queens(0), [[]])

    def test_n_queens_no_solution_for_two(self):
        self.assertEqual(solve_n_queens(2), [])

    def test_n_queens_no_solution_for_three(self):
        self.assertEqual(solve_n_queens(3), [])

    def test_n_queens_one_board(self):
        self.assertEqual(solve_n_queens(1), [[0]])

    def test_n_queens_four_has_two_solutions(self):
        solutions = solve_n_queens(4)
        self.assertEqual(len(solutions), 2)
        self.assertIn([1, 3, 0, 2], solutions)
        self.assertIn([2, 0, 3, 1], solutions)

    def test_n_queens_eight_has_92_solutions(self):
        # 8-Queens is the classically cited case: 92 distinct solutions.
        solutions = solve_n_queens(8)
        self.assertEqual(len(solutions), 92)

    def test_n_queens_solutions_are_valid(self):
        # Every solution must place one queen per row/column with no two
        # queens sharing a diagonal.
        for solution in solve_n_queens(6):
            n = len(solution)
            self.assertEqual(len(set(solution)), n)  # no shared columns
            diagonals = [row - col for row, col in enumerate(solution)]
            anti_diagonals = [row + col for row, col in enumerate(solution)]
            self.assertEqual(len(set(diagonals)), n)
            self.assertEqual(len(set(anti_diagonals)), n)

    def test_n_queens_negative_raises(self):
        with self.assertRaises(ValueError):
            solve_n_queens(-1)


if __name__ == "__main__":
    unittest.main()
