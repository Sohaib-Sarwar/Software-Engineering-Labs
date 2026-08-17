"""
recursion_examples.py

Three classic examples of recursion:
    - factorial: simple linear recursion.
    - fibonacci: recursion with memoization to avoid exponential blowup.
    - solve_n_queens: backtracking recursion over a search tree.
"""

from typing import Dict, List, Optional

# Module-level cache shared across calls to fibonacci(). Keeping it at
# module scope (rather than recomputing a fresh cache per call) means
# repeated calls in the same process reuse previously computed values.
_fibonacci_cache: Dict[int, int] = {0: 0, 1: 1}


def factorial(n: int) -> int:
    """
    Compute n! (n factorial) recursively.

    :param n: A non-negative integer.
    :return: The factorial of ``n``. factorial(0) == 1.
    :raises ValueError: If ``n`` is negative.
    """
    if n < 0:
        raise ValueError("factorial is not defined for negative numbers")
    if n in (0, 1):
        return 1
    return n * factorial(n - 1)


def fibonacci(n: int, cache: Optional[Dict[int, int]] = None) -> int:
    """
    Compute the n-th Fibonacci number (0-indexed: fib(0) = 0, fib(1) = 1)
    using recursion with memoization.

    Without memoization, naive recursive Fibonacci re-computes the same
    sub-problems exponentially many times. Here, previously computed
    results are stored in ``cache`` (a module-level dict by default) so
    each unique sub-problem is solved only once, giving O(n) time.

    :param n: A non-negative integer index into the Fibonacci sequence.
    :param cache: Optional dict used to memoize results. Defaults to a
        shared module-level cache; pass your own dict for an isolated,
        one-off cache.
    :return: The n-th Fibonacci number.
    :raises ValueError: If ``n`` is negative.
    """
    if n < 0:
        raise ValueError("fibonacci is not defined for negative numbers")

    if cache is None:
        cache = _fibonacci_cache

    if n in cache:
        return cache[n]

    cache[n] = fibonacci(n - 1, cache) + fibonacci(n - 2, cache)
    return cache[n]


def solve_n_queens(board_size: int) -> List[List[int]]:
    """
    Solve the N-Queens problem for a board of size ``board_size`` x
    ``board_size`` using backtracking recursion.

    Each solution is represented as a list of length ``board_size``
    where the value at index ``row`` is the column (0-indexed) of the
    queen placed in that row. For example, [1, 3, 0, 2] means: a queen
    in row 0 at column 1, a queen in row 1 at column 3, a queen in row
    2 at column 0, and a queen in row 3 at column 2.

    :param board_size: The size of the (square) chessboard and the
        number of queens to place. board_size == 0 returns a single
        trivial empty solution ([]).
    :return: A list of all distinct solutions. Returns an empty list if
        no solution exists (e.g. board_size == 2 or board_size == 3).
    :raises ValueError: If ``board_size`` is negative.
    """
    if board_size < 0:
        raise ValueError("board_size must be non-negative")
    if board_size == 0:
        return [[]]

    solutions: List[List[int]] = []
    columns_used: set = set()
    diagonals_used: set = set()      # row - col is constant on a "\" diagonal
    anti_diagonals_used: set = set()  # row + col is constant on a "/" diagonal
    placement: List[int] = []

    def backtrack(row: int) -> None:
        if row == board_size:
            solutions.append(placement.copy())
            return

        for col in range(board_size):
            diag = row - col
            anti_diag = row + col

            if (
                col in columns_used
                or diag in diagonals_used
                or anti_diag in anti_diagonals_used
            ):
                continue

            # Place the queen.
            columns_used.add(col)
            diagonals_used.add(diag)
            anti_diagonals_used.add(anti_diag)
            placement.append(col)

            backtrack(row + 1)

            # Undo the placement (backtrack) and try the next column.
            columns_used.remove(col)
            diagonals_used.remove(diag)
            anti_diagonals_used.remove(anti_diag)
            placement.pop()

    backtrack(0)
    return solutions


if __name__ == "__main__":
    print("factorial(5) =", factorial(5))
    print("fibonacci(10) =", fibonacci(10))

    n = 6
    solutions = solve_n_queens(n)
    print(f"solve_n_queens({n}) found {len(solutions)} solutions")
    if solutions:
        print("First solution:", solutions[0])
