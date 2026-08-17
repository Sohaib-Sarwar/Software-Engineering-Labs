"""
calculator.py - a small, dependency-free calculator module.

Provides five basic arithmetic operations: add, subtract, multiply,
divide, and power. Every function validates that its inputs are real
numbers (int or float, not bool) and raises a clear, specific
exception on invalid input:

    - TypeError          if either operand isn't a real number (int/float)
    - ZeroDivisionError  if a division (or a zero base raised to a
                         negative power) would divide by zero

This module is deliberately dependency-free (Python standard library
only) so it can be imported and unit-tested without installing
anything.
"""

from numbers import Real

__all__ = ["add", "subtract", "multiply", "divide", "power"]


def _check_numeric(*values):
    """Raise TypeError if any value is not a real number.

    bool is intentionally rejected even though bool is a subclass of
    int in Python, because passing True/False into a calculator is
    almost always a programming mistake rather than an intended
    numeric value.
    """
    for value in values:
        if isinstance(value, bool) or not isinstance(value, Real):
            raise TypeError(
                "Expected a real number (int or float), got "
                f"{type(value).__name__}: {value!r}"
            )


def add(a, b):
    """Return a + b.

    Raises:
        TypeError: if a or b is not a real number.
    """
    _check_numeric(a, b)
    return a + b


def subtract(a, b):
    """Return a - b.

    Raises:
        TypeError: if a or b is not a real number.
    """
    _check_numeric(a, b)
    return a - b


def multiply(a, b):
    """Return a * b.

    Raises:
        TypeError: if a or b is not a real number.
    """
    _check_numeric(a, b)
    return a * b


def divide(a, b):
    """Return a / b.

    Raises:
        ZeroDivisionError: if b == 0. This is raised explicitly (with a
            clear, descriptive message) instead of relying on Python's
            built-in exception for the bare '/' operator, so every
            caller of this module gets a consistent, documented error.
        TypeError: if a or b is not a real number.
    """
    _check_numeric(a, b)
    if b == 0:
        raise ZeroDivisionError("division by zero: 'b' must not be 0")
    return a / b


def power(base, exponent):
    """Return base ** exponent.

    Raises:
        ZeroDivisionError: if base == 0 and exponent < 0. Mathematically,
            0 raised to a negative power is equivalent to dividing by
            zero (0 ** -1 == 1 / 0 ** 1 == 1 / 0), so this is reported
            as a ZeroDivisionError rather than letting Python raise a
            less descriptive error.
        TypeError: if base or exponent is not a real number.
    """
    _check_numeric(base, exponent)
    if base == 0 and exponent < 0:
        raise ZeroDivisionError(
            "0 cannot be raised to a negative power "
            "(equivalent to division by zero)"
        )
    return base ** exponent
