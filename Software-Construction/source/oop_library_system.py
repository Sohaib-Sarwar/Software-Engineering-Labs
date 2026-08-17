"""
oop_library_system.py
======================

A small library-management domain model used to demonstrate the three
pillars of object-oriented programming that are most relevant to everyday
software construction:

* **Encapsulation** -- internal state (e.g. a ``Book``'s available copy
  count, a ``Member``'s current loans) is kept private and only mutated
  through methods that protect the object's invariants.
* **Inheritance** -- ``Member`` is specialised into ``StandardMember`` and
  ``PremiumMember``, which share common behaviour but override the parts
  that differ (how many books they may borrow at once, how many days they
  may keep a book).
* **Polymorphism** -- ``LendingLibrary`` calls ``member.max_loans()`` and
  ``member.loan_period_days()`` without caring which concrete subclass it
  is talking to; each subclass supplies its own behaviour behind the same
  interface.

The module is dependency-free (Python standard library only) and is fully
runnable/importable, so it can be exercised directly by the unit tests in
``tests/test_oop_library_system.py``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Domain exceptions
# ---------------------------------------------------------------------------

class LibraryError(Exception):
    """Base class for all domain-specific errors raised by this module."""


class BookNotAvailableError(LibraryError):
    """Raised when a book has no remaining copies to lend out."""


class BookNotFoundError(LibraryError):
    """Raised when an operation references a book that is not catalogued."""


class MemberNotFoundError(LibraryError):
    """Raised when an operation references a member who is not registered."""


class LoanLimitExceededError(LibraryError):
    """Raised when a member tries to borrow beyond their personal limit."""


class LoanNotFoundError(LibraryError):
    """Raised when trying to return/renew a loan that does not exist."""


# ---------------------------------------------------------------------------
# Book: encapsulation of copy-count state
# ---------------------------------------------------------------------------

class Book:
    """Represents a title held by the library, possibly in multiple copies.

    The number of copies currently on loan is private state (``__copies_on_loan``)
    so that external code cannot corrupt it directly; it can only change via
    :meth:`checkout_copy` and :meth:`return_copy`, which enforce the
    invariant ``0 <= copies_on_loan <= total_copies``.
    """

    def __init__(self, isbn: str, title: str, author: str, total_copies: int = 1) -> None:
        if not isbn:
            raise ValueError("isbn must be a non-empty string")
        if not title:
            raise ValueError("title must be a non-empty string")
        if not author:
            raise ValueError("author must be a non-empty string")
        if total_copies < 1:
            raise ValueError("total_copies must be at least 1")

        self._isbn = isbn
        self._title = title
        self._author = author
        self._total_copies = total_copies
        self.__copies_on_loan = 0  # name-mangled: truly private to Book

    # -- read-only public view of identity -------------------------------
    @property
    def isbn(self) -> str:
        return self._isbn

    @property
    def title(self) -> str:
        return self._title

    @property
    def author(self) -> str:
        return self._author

    @property
    def total_copies(self) -> int:
        return self._total_copies

    @property
    def copies_on_loan(self) -> int:
        return self.__copies_on_loan

    @property
    def available_copies(self) -> int:
        return self._total_copies - self.__copies_on_loan

    def is_available(self) -> bool:
        return self.available_copies > 0

    # -- controlled state mutation ----------------------------------------
    def checkout_copy(self) -> None:
        """Mark one copy as on loan. Raises if none are available."""
        if not self.is_available():
            raise BookNotAvailableError(f"No available copies of '{self._title}'")
        self.__copies_on_loan += 1

    def return_copy(self) -> None:
        """Mark one on-loan copy as returned. Raises if that would be invalid."""
        if self.__copies_on_loan <= 0:
            raise LibraryError(f"All copies of '{self._title}' are already checked in")
        self.__copies_on_loan -= 1

    def add_copies(self, count: int) -> None:
        """Increase the catalogue's total copy count (e.g. new stock arrives)."""
        if count <= 0:
            raise ValueError("count must be positive")
        self._total_copies += count

    def __repr__(self) -> str:  # pragma: no cover - debugging aid only
        return f"Book(isbn={self._isbn!r}, title={self._title!r}, available={self.available_copies}/{self._total_copies})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Book) and other.isbn == self.isbn

    def __hash__(self) -> int:
        return hash(self._isbn)


# ---------------------------------------------------------------------------
# Member hierarchy: inheritance + polymorphism
# ---------------------------------------------------------------------------

class Member(ABC):
    """Abstract base class for all library members.

    Subclasses must supply the two policy hooks (:meth:`max_loans` and
    :meth:`loan_period_days`) that determine how the member is treated by
    :class:`LendingLibrary`. This is the classic "template hook" shape of
    polymorphism: the library code is written once, against ``Member``, and
    behaves differently depending on the concrete subclass supplied at
    runtime.
    """

    def __init__(self, member_id: str, name: str) -> None:
        if not member_id:
            raise ValueError("member_id must be a non-empty string")
        if not name:
            raise ValueError("name must be a non-empty string")
        self._member_id = member_id
        self._name = name
        self._active_loan_isbns: List[str] = []

    @property
    def member_id(self) -> str:
        return self._member_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def active_loan_count(self) -> int:
        return len(self._active_loan_isbns)

    @abstractmethod
    def max_loans(self) -> int:
        """Maximum number of books this member may have out simultaneously."""
        raise NotImplementedError

    @abstractmethod
    def loan_period_days(self) -> int:
        """Number of days this member is allowed to keep a borrowed book."""
        raise NotImplementedError

    def has_reached_loan_limit(self) -> bool:
        return self.active_loan_count >= self.max_loans()

    # -- internal bookkeeping used only by LendingLibrary ------------------
    def _record_loan(self, isbn: str) -> None:
        self._active_loan_isbns.append(isbn)

    def _release_loan(self, isbn: str) -> None:
        self._active_loan_isbns.remove(isbn)

    def __repr__(self) -> str:  # pragma: no cover - debugging aid only
        return f"{type(self).__name__}(member_id={self._member_id!r}, name={self._name!r})"


class StandardMember(Member):
    """A regular member: modest borrowing limit and standard loan period."""

    _MAX_LOANS = 3
    _LOAN_PERIOD_DAYS = 14

    def max_loans(self) -> int:
        return self._MAX_LOANS

    def loan_period_days(self) -> int:
        return self._LOAN_PERIOD_DAYS


class PremiumMember(Member):
    """A paying member: higher borrowing limit and a longer loan period."""

    _MAX_LOANS = 10
    _LOAN_PERIOD_DAYS = 28

    def max_loans(self) -> int:
        return self._MAX_LOANS

    def loan_period_days(self) -> int:
        return self._LOAN_PERIOD_DAYS


class LibrarianMember(Member):
    """Library staff: effectively unlimited loans, generous loan period.

    Demonstrates that a third, independently-written subclass slots into
    the same polymorphic interface with no changes required elsewhere.
    """

    _MAX_LOANS = 1000
    _LOAN_PERIOD_DAYS = 60

    def max_loans(self) -> int:
        return self._MAX_LOANS

    def loan_period_days(self) -> int:
        return self._LOAN_PERIOD_DAYS


# ---------------------------------------------------------------------------
# Loan: a value-ish record tying a Book to a Member over a date range
# ---------------------------------------------------------------------------

@dataclass
class Loan:
    """An immutable-in-spirit record of a single borrowing transaction."""

    isbn: str
    member_id: str
    checkout_date: date
    due_date: date
    returned_date: Optional[date] = field(default=None)

    def is_returned(self) -> bool:
        return self.returned_date is not None

    def is_overdue(self, as_of: date) -> bool:
        if self.is_returned():
            return False
        return as_of > self.due_date

    def days_overdue(self, as_of: date) -> int:
        if not self.is_overdue(as_of):
            return 0
        return (as_of - self.due_date).days


# ---------------------------------------------------------------------------
# LendingLibrary: the manager class enforcing cross-object invariants
# ---------------------------------------------------------------------------

class LendingLibrary:
    """Coordinates books and members, enforcing the library's business rules.

    Invariants enforced here (not inside ``Book`` or ``Member`` alone,
    because they involve *both*):

    * A member may never hold more active loans than their ``max_loans()``.
    * A book may never be checked out to a member who already has an open
      loan for that exact title.
    * Returning or renewing a loan that does not exist raises an error.
    """

    def __init__(self) -> None:
        self._books: Dict[str, Book] = {}
        self._members: Dict[str, Member] = {}
        self._active_loans: Dict[tuple, Loan] = {}  # (isbn, member_id) -> Loan
        self._loan_history: List[Loan] = []

    # -- catalogue / registry management -----------------------------------
    def add_book(self, book: Book) -> None:
        self._books[book.isbn] = book

    def register_member(self, member: Member) -> None:
        self._members[member.member_id] = member

    def get_book(self, isbn: str) -> Book:
        try:
            return self._books[isbn]
        except KeyError:
            raise BookNotFoundError(f"No book catalogued with isbn {isbn!r}") from None

    def get_member(self, member_id: str) -> Member:
        try:
            return self._members[member_id]
        except KeyError:
            raise MemberNotFoundError(f"No member registered with id {member_id!r}") from None

    # -- core lending workflow ----------------------------------------------
    def checkout_book(self, isbn: str, member_id: str, *, today: Optional[date] = None) -> Loan:
        """Check a book out to a member, returning the created :class:`Loan`.

        Raises ``BookNotAvailableError``, ``LoanLimitExceededError`` or a
        ``LibraryError`` if the member already has this exact book out.
        """
        today = today or date.today()
        book = self.get_book(isbn)
        member = self.get_member(member_id)

        key = (isbn, member_id)
        if key in self._active_loans:
            raise LibraryError(f"Member {member_id!r} already has an active loan for {isbn!r}")

        if member.has_reached_loan_limit():
            raise LoanLimitExceededError(
                f"Member {member_id!r} has reached their limit of {member.max_loans()} loans"
            )

        # This raises BookNotAvailableError if there is no stock; note we
        # perform the availability check *before* touching member state so
        # that a failed checkout leaves every object unchanged (atomicity).
        book.checkout_copy()

        due_date = today + timedelta(days=member.loan_period_days())
        loan = Loan(isbn=isbn, member_id=member_id, checkout_date=today, due_date=due_date)

        member._record_loan(isbn)
        self._active_loans[key] = loan
        return loan

    def return_book(self, isbn: str, member_id: str, *, today: Optional[date] = None) -> Loan:
        """Return a previously checked-out book, closing its loan record."""
        today = today or date.today()
        key = (isbn, member_id)
        try:
            loan = self._active_loans.pop(key)
        except KeyError:
            raise LoanNotFoundError(
                f"No active loan for isbn {isbn!r} and member {member_id!r}"
            ) from None

        book = self.get_book(isbn)
        member = self.get_member(member_id)

        book.return_copy()
        member._release_loan(isbn)
        loan.returned_date = today
        self._loan_history.append(loan)
        return loan

    def renew_loan(self, isbn: str, member_id: str, *, today: Optional[date] = None) -> Loan:
        """Extend a loan's due date by the member's standard loan period.

        Renewal is refused once the loan is already overdue -- a simple
        business rule that keeps overdue books from being renewed
        indefinitely.
        """
        today = today or date.today()
        key = (isbn, member_id)
        try:
            loan = self._active_loans[key]
        except KeyError:
            raise LoanNotFoundError(
                f"No active loan for isbn {isbn!r} and member {member_id!r}"
            ) from None

        if loan.is_overdue(today):
            raise LibraryError("Cannot renew an overdue loan; return it first")

        member = self.get_member(member_id)
        loan.due_date = loan.due_date + timedelta(days=member.loan_period_days())
        return loan

    # -- reporting helpers ----------------------------------------------------
    def active_loans_for_member(self, member_id: str) -> List[Loan]:
        return [loan for (isbn, mid), loan in self._active_loans.items() if mid == member_id]

    def overdue_loans(self, *, today: Optional[date] = None) -> List[Loan]:
        today = today or date.today()
        return [loan for loan in self._active_loans.values() if loan.is_overdue(today)]

    def available_books(self) -> List[Book]:
        return [book for book in self._books.values() if book.is_available()]
