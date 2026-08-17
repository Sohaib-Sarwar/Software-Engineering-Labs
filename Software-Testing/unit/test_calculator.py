"""
test_calculator.py - unit tests for calculator.py

Run just this file:
    python -m unittest unit.test_calculator -v

Run the whole test suite from the Software-Testing folder:
    python -m unittest discover

These tests are organised using equivalence partitioning (grouping
inputs into classes that should behave the same way: "normal numbers",
"negative numbers", "zero", "invalid types", ...) plus boundary value
analysis for the values that sit right on the edge of a rule change
(for example b == 0 in divide(), and exponent == 0 / exponent < 0 in
power()). See documentation/README.md for a full explanation of the
technique with a worked example.
"""

import os
import sys
import unittest

# Make sure "calculator" (a sibling module in this same directory) can be
# imported no matter how this test file is invoked: directly
# (python test_calculator.py), as a scoped discovery run from inside
# unit/ (python -m unittest discover), or as part of the whole-project
# discovery run from the Software-Testing/ root
# (python -m unittest discover), where this file is imported as the
# package module "unit.test_calculator" and a bare "import calculator"
# would otherwise fail because unit/ itself is not on sys.path.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from calculator import add, subtract, multiply, divide, power


class TestAdd(unittest.TestCase):
    """Equivalence partitions: positive+positive, positive+negative,
    negative+negative, zero, floats."""

    def test_two_positive_integers(self):
        self.assertEqual(add(2, 3), 5)

    def test_positive_and_negative(self):
        self.assertEqual(add(5, -3), 2)

    def test_two_negative_integers(self):
        self.assertEqual(add(-4, -6), -10)

    def test_with_zero(self):
        self.assertEqual(add(0, 7), 7)
        self.assertEqual(add(7, 0), 7)
        self.assertEqual(add(0, 0), 0)

    def test_with_floats(self):
        self.assertAlmostEqual(add(2.5, 0.25), 2.75)

    def test_rejects_non_numeric_input(self):
        with self.assertRaises(TypeError):
            add("2", 3)
        with self.assertRaises(TypeError):
            add(2, None)
        with self.assertRaises(TypeError):
            add([1], 2)

    def test_rejects_bool_input(self):
        # bool is a subclass of int in Python; the calculator explicitly
        # rejects it since True/False are not intended numeric inputs.
        with self.assertRaises(TypeError):
            add(True, 1)
        with self.assertRaises(TypeError):
            add(1, False)


class TestSubtract(unittest.TestCase):
    def test_positive_minus_smaller_positive(self):
        self.assertEqual(subtract(10, 4), 6)

    def test_result_is_negative(self):
        self.assertEqual(subtract(4, 10), -6)

    def test_subtracting_negative_number(self):
        self.assertEqual(subtract(5, -5), 10)

    def test_with_zero(self):
        self.assertEqual(subtract(9, 0), 9)
        self.assertEqual(subtract(0, 9), -9)

    def test_with_floats(self):
        self.assertAlmostEqual(subtract(5.5, 2.2), 3.3)

    def test_rejects_non_numeric_input(self):
        with self.assertRaises(TypeError):
            subtract("10", "4")
        with self.assertRaises(TypeError):
            subtract(None, 4)


class TestMultiply(unittest.TestCase):
    def test_two_positive_integers(self):
        self.assertEqual(multiply(3, 4), 12)

    def test_positive_times_negative(self):
        self.assertEqual(multiply(3, -4), -12)

    def test_two_negative_integers(self):
        self.assertEqual(multiply(-3, -4), 12)

    def test_multiply_by_zero(self):
        self.assertEqual(multiply(0, 999), 0)
        self.assertEqual(multiply(999, 0), 0)

    def test_multiply_by_one_is_identity(self):
        self.assertEqual(multiply(1, 42), 42)
        self.assertEqual(multiply(42, 1), 42)

    def test_with_floats(self):
        self.assertAlmostEqual(multiply(2.5, 4), 10.0)

    def test_rejects_non_numeric_input(self):
        with self.assertRaises(TypeError):
            multiply({}, 2)
        with self.assertRaises(TypeError):
            multiply(2, "x")


class TestDivide(unittest.TestCase):
    """Equivalence partitions for divide(a, b):
        - b is a normal non-zero number (positive or negative) -> a / b
        - b == 0 (the boundary case) -> ZeroDivisionError
        - a or b is not a real number -> TypeError
    """

    def test_normal_division(self):
        self.assertEqual(divide(10, 2), 5)

    def test_division_resulting_in_float(self):
        self.assertAlmostEqual(divide(7, 2), 3.5)

    def test_division_with_negative_numbers(self):
        self.assertEqual(divide(-10, 2), -5)
        self.assertEqual(divide(10, -2), -5)
        self.assertEqual(divide(-10, -2), 5)

    def test_zero_divided_by_nonzero_is_zero(self):
        self.assertEqual(divide(0, 5), 0)

    def test_divide_by_zero_raises_zero_division_error(self):
        # This is the critical boundary case for this module: b == 0.
        with self.assertRaises(ZeroDivisionError) as ctx:
            divide(10, 0)
        self.assertIn("division by zero", str(ctx.exception))

    def test_divide_by_zero_with_zero_numerator_still_raises(self):
        # 0 / 0 is undefined too - must still raise, not return NaN.
        with self.assertRaises(ZeroDivisionError):
            divide(0, 0)

    def test_divide_with_floats(self):
        self.assertAlmostEqual(divide(5.0, 2.0), 2.5)

    def test_rejects_non_numeric_input(self):
        with self.assertRaises(TypeError):
            divide("10", 2)
        with self.assertRaises(TypeError):
            divide(10, None)

    def test_rejects_bool_input(self):
        with self.assertRaises(TypeError):
            divide(True, 2)


class TestPower(unittest.TestCase):
    """Equivalence partitions for power(base, exponent):
        - exponent > 0 (normal case)
        - exponent == 0 (boundary: any nonzero base -> 1)
        - exponent < 0 (negative exponent -> reciprocal)
        - base == 0 with exponent > 0 -> 0
        - base == 0 with exponent == 0 -> 1 (Python convention)
        - base == 0 with exponent < 0 -> ZeroDivisionError (boundary)
    """

    def test_positive_base_positive_exponent(self):
        self.assertEqual(power(2, 3), 8)

    def test_negative_base_even_exponent(self):
        self.assertEqual(power(-2, 2), 4)

    def test_negative_base_odd_exponent(self):
        self.assertEqual(power(-2, 3), -8)

    def test_any_nonzero_base_to_the_zero_power_is_one(self):
        self.assertEqual(power(5, 0), 1)
        self.assertEqual(power(-5, 0), 1)

    def test_negative_exponent_returns_reciprocal(self):
        self.assertAlmostEqual(power(2, -2), 0.25)

    def test_zero_base_positive_exponent_is_zero(self):
        self.assertEqual(power(0, 5), 0)

    def test_zero_base_zero_exponent_is_one_by_convention(self):
        # Python (and this module) follow the common convention 0**0 == 1.
        self.assertEqual(power(0, 0), 1)

    def test_zero_base_negative_exponent_raises_zero_division_error(self):
        # This is the critical boundary case for this function.
        with self.assertRaises(ZeroDivisionError) as ctx:
            power(0, -1)
        self.assertIn("negative power", str(ctx.exception))

    def test_with_floats(self):
        self.assertAlmostEqual(power(2.0, 0.5), 1.4142135623730951)

    def test_rejects_non_numeric_input(self):
        with self.assertRaises(TypeError):
            power("2", 3)
        with self.assertRaises(TypeError):
            power(2, "3")

    def test_rejects_bool_input(self):
        with self.assertRaises(TypeError):
            power(True, 2)


if __name__ == "__main__":
    unittest.main()
