"""
Unit tests for source/oop_library_system.py.

Written against the standard library's ``unittest`` so they run with either

    python -m unittest discover tests

or, if pytest happens to be installed, simply

    pytest tests/test_oop_library_system.py

(pytest natively collects and runs ``unittest.TestCase`` subclasses).
"""

import os
import sys
import unittest
from datetime import date, timedelta

# Make the sibling "source" package importable regardless of the current
# working directory the test runner was invoked from.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from source.oop_library_system import (
    Book,
    BookNotAvailableError,
    BookNotFoundError,
    LendingLibrary,
    LibraryError,
    LibrarianMember,
    LoanLimitExceededError,
    LoanNotFoundError,
    MemberNotFoundError,
    PremiumMember,
    StandardMember,
)


class BookTests(unittest.TestCase):
    def test_new_book_is_fully_available(self):
        book = Book("111", "Clean Code", "Robert C. Martin", total_copies=2)
        self.assertEqual(book.available_copies, 2)
        self.assertTrue(book.is_available())

    def test_checkout_copy_reduces_availability(self):
        book = Book("111", "Clean Code", "Robert C. Martin", total_copies=2)
        book.checkout_copy()
        self.assertEqual(book.available_copies, 1)
        self.assertEqual(book.copies_on_loan, 1)

    def test_checkout_copy_raises_when_none_available(self):
        book = Book("111", "Clean Code", "Robert C. Martin", total_copies=1)
        book.checkout_copy()
        with self.assertRaises(BookNotAvailableError):
            book.checkout_copy()

    def test_return_copy_raises_when_nothing_on_loan(self):
        book = Book("111", "Clean Code", "Robert C. Martin", total_copies=1)
        with self.assertRaises(LibraryError):
            book.return_copy()

    def test_return_copy_restores_availability(self):
        book = Book("111", "Clean Code", "Robert C. Martin", total_copies=1)
        book.checkout_copy()
        book.return_copy()
        self.assertEqual(book.available_copies, 1)

    def test_add_copies_increases_total(self):
        book = Book("111", "Clean Code", "Robert C. Martin", total_copies=1)
        book.add_copies(2)
        self.assertEqual(book.total_copies, 3)
        self.assertEqual(book.available_copies, 3)

    def test_invalid_construction_raises_value_error(self):
        with self.assertRaises(ValueError):
            Book("", "Title", "Author")
        with self.assertRaises(ValueError):
            Book("111", "", "Author")
        with self.assertRaises(ValueError):
            Book("111", "Title", "")
        with self.assertRaises(ValueError):
            Book("111", "Title", "Author", total_copies=0)

    def test_equality_is_based_on_isbn(self):
        a = Book("111", "Title", "Author")
        b = Book("111", "Different Title", "Different Author")
        c = Book("222", "Title", "Author")
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)


class MemberHierarchyTests(unittest.TestCase):
    def test_standard_member_policy(self):
        member = StandardMember("M1", "Alice")
        self.assertEqual(member.max_loans(), 3)
        self.assertEqual(member.loan_period_days(), 14)

    def test_premium_member_policy(self):
        member = PremiumMember("M2", "Bob")
        self.assertEqual(member.max_loans(), 10)
        self.assertEqual(member.loan_period_days(), 28)

    def test_librarian_member_policy(self):
        member = LibrarianMember("M3", "Carol")
        self.assertEqual(member.max_loans(), 1000)
        self.assertEqual(member.loan_period_days(), 60)

    def test_has_reached_loan_limit_is_polymorphic(self):
        # Two different subclasses, exercised through the same base-class
        # interface, must each honour their own limit.
        standard = StandardMember("M1", "Alice")
        premium = PremiumMember("M2", "Bob")
        for _ in range(3):
            standard._record_loan("some-isbn")
        self.assertTrue(standard.has_reached_loan_limit())
        self.assertFalse(premium.has_reached_loan_limit())

    def test_invalid_construction_raises_value_error(self):
        with self.assertRaises(ValueError):
            StandardMember("", "Alice")
        with self.assertRaises(ValueError):
            StandardMember("M1", "")


class LendingLibraryTests(unittest.TestCase):
    def setUp(self):
        self.library = LendingLibrary()
        self.book = Book("111", "Clean Code", "Robert C. Martin", total_copies=1)
        self.member = StandardMember("M1", "Alice")
        self.library.add_book(self.book)
        self.library.register_member(self.member)
        self.today = date(2024, 1, 1)

    def test_get_book_missing_raises(self):
        with self.assertRaises(BookNotFoundError):
            self.library.get_book("does-not-exist")

    def test_get_member_missing_raises(self):
        with self.assertRaises(MemberNotFoundError):
            self.library.get_member("does-not-exist")

    def test_checkout_book_creates_loan_with_correct_due_date(self):
        loan = self.library.checkout_book("111", "M1", today=self.today)
        self.assertEqual(loan.checkout_date, self.today)
        self.assertEqual(loan.due_date, self.today + timedelta(days=14))
        self.assertFalse(loan.is_returned())
        self.assertEqual(self.book.available_copies, 0)
        self.assertEqual(self.member.active_loan_count, 1)

    def test_checkout_unavailable_book_raises(self):
        self.library.checkout_book("111", "M1", today=self.today)
        other_member = StandardMember("M2", "Bob")
        self.library.register_member(other_member)
        with self.assertRaises(BookNotAvailableError):
            self.library.checkout_book("111", "M2", today=self.today)

    def test_checkout_same_book_twice_by_same_member_raises(self):
        self.book.add_copies(1)  # ensure a second copy exists
        self.library.checkout_book("111", "M1", today=self.today)
        with self.assertRaises(LibraryError):
            self.library.checkout_book("111", "M1", today=self.today)

    def test_checkout_at_capacity_raises_loan_limit_exceeded(self):
        # Standard members may hold at most 3 books; give them exactly 3
        # different titles, then attempt a 4th checkout.
        for n in range(3):
            isbn = f"9{n}"
            book = Book(isbn, f"Book {n}", "Some Author", total_copies=1)
            self.library.add_book(book)
            self.library.checkout_book(isbn, "M1", today=self.today)

        self.assertTrue(self.member.has_reached_loan_limit())
        with self.assertRaises(LoanLimitExceededError):
            self.library.checkout_book("111", "M1", today=self.today)

        # The book's own availability must be untouched by the failed attempt.
        self.assertEqual(self.book.available_copies, 1)

    def test_return_book_restores_state(self):
        self.library.checkout_book("111", "M1", today=self.today)
        return_date = self.today + timedelta(days=5)
        loan = self.library.return_book("111", "M1", today=return_date)
        self.assertTrue(loan.is_returned())
        self.assertEqual(loan.returned_date, return_date)
        self.assertEqual(self.book.available_copies, 1)
        self.assertEqual(self.member.active_loan_count, 0)

    def test_return_book_without_active_loan_raises(self):
        with self.assertRaises(LoanNotFoundError):
            self.library.return_book("111", "M1", today=self.today)

    def test_renew_loan_extends_due_date(self):
        loan = self.library.checkout_book("111", "M1", today=self.today)
        original_due_date = loan.due_date
        self.library.renew_loan("111", "M1", today=self.today)
        self.assertEqual(loan.due_date, original_due_date + timedelta(days=14))

    def test_renew_overdue_loan_raises(self):
        loan = self.library.checkout_book("111", "M1", today=self.today)
        way_overdue = loan.due_date + timedelta(days=1)
        with self.assertRaises(LibraryError):
            self.library.renew_loan("111", "M1", today=way_overdue)

    def test_renew_missing_loan_raises(self):
        with self.assertRaises(LoanNotFoundError):
            self.library.renew_loan("111", "M1", today=self.today)

    def test_overdue_loans_reports_only_overdue_ones(self):
        self.book.add_copies(1)
        loan = self.library.checkout_book("111", "M1", today=self.today)
        past_due_check_date = loan.due_date + timedelta(days=1)
        overdue = self.library.overdue_loans(today=past_due_check_date)
        self.assertEqual(len(overdue), 1)
        self.assertIs(overdue[0], loan)

    def test_available_books_excludes_fully_checked_out_titles(self):
        self.assertIn(self.book, self.library.available_books())
        self.library.checkout_book("111", "M1", today=self.today)
        self.assertNotIn(self.book, self.library.available_books())

    def test_active_loans_for_member(self):
        self.book.add_copies(1)
        second_book = Book("222", "Refactoring", "Martin Fowler", total_copies=1)
        self.library.add_book(second_book)
        self.library.checkout_book("111", "M1", today=self.today)
        self.library.checkout_book("222", "M1", today=self.today)
        loans = self.library.active_loans_for_member("M1")
        self.assertEqual(len(loans), 2)
        isbns = {loan.isbn for loan in loans}
        self.assertEqual(isbns, {"111", "222"})


if __name__ == "__main__":
    unittest.main()
