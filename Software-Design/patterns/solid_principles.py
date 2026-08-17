"""
solid_principles.py

Five short, self-contained BEFORE/AFTER pairs, one per SOLID principle:

    S - Single Responsibility Principle
    O - Open/Closed Principle
    L - Liskov Substitution Principle
    I - Interface Segregation Principle
    D - Dependency Inversion Principle

Each pair is a small "violation" implementation followed by a "fix"
implementation. Every class actually runs; there are no stubs or
placeholders. Run this file directly to see each demo execute in turn:

    python solid_principles.py

Standard library only - no third-party dependencies.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


def section(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


# ---------------------------------------------------------------------------
# 1. SINGLE RESPONSIBILITY PRINCIPLE (SRP)
#
# "A class should have only one reason to change."
# ---------------------------------------------------------------------------

# --- BEFORE: violates SRP -----------------------------------------------
#
# InvoiceBad has two reasons to change:
#   1. the business rules for computing invoice totals change
#   2. the way invoices are persisted (e.g. file format) changes
# Formatting/text-rendering and persistence are mixed into one class.

class InvoiceBad:
    def __init__(self, customer: str, amount: float):
        self.customer = customer
        self.amount = amount

    def total_with_tax(self, tax_rate: float = 0.15) -> float:
        return self.amount * (1 + tax_rate)

    def render_text(self) -> str:
        return f"Invoice for {self.customer}: ${self.total_with_tax():.2f}"

    def save_to_file(self, path: str) -> None:
        # Persistence concern baked directly into the invoice class.
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.render_text())


# --- AFTER: follows SRP ---------------------------------------------------
#
# Each class now has exactly one reason to change:
#   Invoice            -> business data + tax calculation
#   InvoiceFormatter    -> how an invoice is rendered as text
#   InvoiceRepository   -> how an invoice is persisted

class Invoice:
    def __init__(self, customer: str, amount: float):
        self.customer = customer
        self.amount = amount

    def total_with_tax(self, tax_rate: float = 0.15) -> float:
        return self.amount * (1 + tax_rate)


class InvoiceFormatter:
    @staticmethod
    def render_text(invoice: Invoice) -> str:
        return f"Invoice for {invoice.customer}: ${invoice.total_with_tax():.2f}"


class InvoiceRepository:
    @staticmethod
    def save_to_file(invoice: Invoice, path: str) -> None:
        text = InvoiceFormatter.render_text(invoice)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)


def demo_srp() -> None:
    section("SRP - Single Responsibility Principle")

    print("-- BEFORE (violation): formatting + persistence in one class --")
    bad = InvoiceBad("Acme Corp", 200.0)
    print(bad.render_text())

    print("\n-- AFTER (fixed): responsibilities split across 3 classes --")
    invoice = Invoice("Acme Corp", 200.0)
    text = InvoiceFormatter.render_text(invoice)
    print(text)
    # Persisting no longer requires touching Invoice or InvoiceFormatter.
    print("(InvoiceRepository.save_to_file would persist the same text)")


# ---------------------------------------------------------------------------
# 2. OPEN/CLOSED PRINCIPLE (OCP)
#
# "Software entities should be open for extension, but closed
# for modification."
# ---------------------------------------------------------------------------

# --- BEFORE: violates OCP --------------------------------------------------
#
# Every time a new customer type is added, this function must be edited.
# That means the "closed for modification" part is violated: existing,
# already-tested code has to change to support a new case.

class DiscountCalculatorBad:
    def discount_for(self, customer_type: str, amount: float) -> float:
        if customer_type == "regular":
            return amount * 0.0
        elif customer_type == "silver":
            return amount * 0.05
        elif customer_type == "gold":
            return amount * 0.10
        else:
            raise ValueError(f"Unknown customer type: {customer_type}")
        # Adding "platinum" means editing this method again.


# --- AFTER: follows OCP -----------------------------------------------------
#
# New discount tiers are added by writing a *new* class that implements
# DiscountStrategy - the calculator itself never needs to change.

class DiscountStrategy(ABC):
    @abstractmethod
    def discount(self, amount: float) -> float:
        raise NotImplementedError


class RegularDiscount(DiscountStrategy):
    def discount(self, amount: float) -> float:
        return amount * 0.0


class SilverDiscount(DiscountStrategy):
    def discount(self, amount: float) -> float:
        return amount * 0.05


class GoldDiscount(DiscountStrategy):
    def discount(self, amount: float) -> float:
        return amount * 0.10


# Extension example: adding Platinum requires zero edits to existing code.
class PlatinumDiscount(DiscountStrategy):
    def discount(self, amount: float) -> float:
        return amount * 0.20


class DiscountCalculator:
    def discount_for(self, strategy: DiscountStrategy, amount: float) -> float:
        return strategy.discount(amount)


def demo_ocp() -> None:
    section("OCP - Open/Closed Principle")

    print("-- BEFORE (violation): if/elif chain must be edited for new tiers --")
    bad_calc = DiscountCalculatorBad()
    for tier in ("regular", "silver", "gold"):
        print(f"{tier:8s}: {bad_calc.discount_for(tier, 100.0):.2f}")

    print("\n-- AFTER (fixed): new tiers extend, never modify, the calculator --")
    calc = DiscountCalculator()
    strategies = {
        "regular": RegularDiscount(),
        "silver": SilverDiscount(),
        "gold": GoldDiscount(),
        "platinum": PlatinumDiscount(),  # added with no changes above
    }
    for name, strategy in strategies.items():
        print(f"{name:8s}: {calc.discount_for(strategy, 100.0):.2f}")


# ---------------------------------------------------------------------------
# 3. LISKOV SUBSTITUTION PRINCIPLE (LSP)
#
# "Objects of a superclass shall be replaceable with objects of a
# subclass without breaking correctness."
# ---------------------------------------------------------------------------

# --- BEFORE: violates LSP ---------------------------------------------------
#
# SquareBad inherits from RectangleBad and overrides the setters so that
# width and height always stay equal. This breaks any code that treats a
# RectangleBad polymorphically, because setting width no longer leaves
# height untouched, violating the base class's contract.

class RectangleBad:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def set_width(self, width: float) -> None:
        self.width = width

    def set_height(self, height: float) -> None:
        self.height = height

    def area(self) -> float:
        return self.width * self.height


class SquareBad(RectangleBad):
    def __init__(self, size: float):
        super().__init__(size, size)

    def set_width(self, width: float) -> None:
        # Forces height to follow width - breaks RectangleBad's contract.
        self.width = width
        self.height = width

    def set_height(self, height: float) -> None:
        # Forces width to follow height - breaks RectangleBad's contract.
        self.width = height
        self.height = height


def resize_and_check_area(rect: RectangleBad) -> float:
    """Any RectangleBad should support this independently of subtype."""
    rect.set_width(5)
    rect.set_height(4)
    return rect.area()  # A caller expects 5 * 4 == 20 for ANY RectangleBad.


# --- AFTER: follows LSP ------------------------------------------------------
#
# Square is no longer forced into a Rectangle's inheritance hierarchy.
# Both are independent implementations of a common Shape abstraction,
# each with its own honest, non-surprising behavior. Substituting any
# Shape for another never breaks a caller's expectations because neither
# type promises mutable, independent width/height in the first place.

class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        raise NotImplementedError


@dataclass
class Rectangle(Shape):
    width: float
    height: float

    def area(self) -> float:
        return self.width * self.height


@dataclass
class Square(Shape):
    size: float

    def area(self) -> float:
        return self.size * self.size


def total_area(shapes: list) -> float:
    """Works correctly no matter which Shape subtypes are passed in."""
    return sum(shape.area() for shape in shapes)


def demo_lsp() -> None:
    section("LSP - Liskov Substitution Principle")

    print("-- BEFORE (violation): Square silently breaks Rectangle's contract --")
    rect = RectangleBad(2, 3)
    print(f"resize_and_check_area(Rectangle) = {resize_and_check_area(rect)} (expected 20)")
    square = SquareBad(2)
    # A caller substituting a SquareBad for a RectangleBad gets a
    # surprising, contract-breaking result:
    print(f"resize_and_check_area(Square)    = {resize_and_check_area(square)} (expected 20, but square logic breaks it)")

    print("\n-- AFTER (fixed): Square and Rectangle are independent Shapes --")
    shapes = [Rectangle(5, 4), Square(5)]
    for shape in shapes:
        print(f"{type(shape).__name__:10s} area = {shape.area()}")
    print(f"total_area(shapes) = {total_area(shapes)} (each shape behaves honestly)")


# ---------------------------------------------------------------------------
# 4. INTERFACE SEGREGATION PRINCIPLE (ISP)
#
# "Clients should not be forced to depend on methods they do not use."
# ---------------------------------------------------------------------------

# --- BEFORE: violates ISP ---------------------------------------------------
#
# WorkerBad forces every implementer to provide both work() and eat(),
# even types (like a robot) for which "eating" makes no sense.

class WorkerBad(ABC):
    @abstractmethod
    def work(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def eat(self) -> str:
        raise NotImplementedError


class HumanWorkerBad(WorkerBad):
    def work(self) -> str:
        return "Human is working"

    def eat(self) -> str:
        return "Human is eating lunch"


class RobotWorkerBad(WorkerBad):
    def work(self) -> str:
        return "Robot is working"

    def eat(self) -> str:
        # Nonsensical, but the fat interface forces this method to exist.
        raise NotImplementedError("Robots do not eat")


# --- AFTER: follows ISP ------------------------------------------------------
#
# The fat interface is split into small, focused interfaces. Clients
# (and implementers) only depend on the capabilities they actually need.

class Workable(ABC):
    @abstractmethod
    def work(self) -> str:
        raise NotImplementedError


class Eatable(ABC):
    @abstractmethod
    def eat(self) -> str:
        raise NotImplementedError


class HumanWorker(Workable, Eatable):
    def work(self) -> str:
        return "Human is working"

    def eat(self) -> str:
        return "Human is eating lunch"


class RobotWorker(Workable):
    # RobotWorker only implements Workable - no unwanted eat() method,
    # and no need to raise NotImplementedError anywhere.
    def work(self) -> str:
        return "Robot is working"


def run_shift(workers: list) -> None:
    for w in workers:
        print(w.work())


def run_lunch_break(eaters: list) -> None:
    for e in eaters:
        print(e.eat())


def demo_isp() -> None:
    section("ISP - Interface Segregation Principle")

    print("-- BEFORE (violation): RobotWorkerBad forced to implement eat() --")
    bad_workers = [HumanWorkerBad(), RobotWorkerBad()]
    for w in bad_workers:
        print(w.work())
    try:
        bad_workers[1].eat()
    except NotImplementedError as exc:
        print(f"Calling eat() on RobotWorkerBad raises: {exc}")

    print("\n-- AFTER (fixed): capabilities split into Workable / Eatable --")
    human = HumanWorker()
    robot = RobotWorker()
    run_shift([human, robot])
    # Only pass things that actually implement Eatable - no runtime surprises.
    run_lunch_break([human])
    print("(robot is simply never asked to eat - no forced/empty method)")


# ---------------------------------------------------------------------------
# 5. DEPENDENCY INVERSION PRINCIPLE (DIP)
#
# "Depend upon abstractions, not concretions."
# ---------------------------------------------------------------------------

# --- BEFORE: violates DIP ----------------------------------------------------
#
# NotificationServiceBad (a high-level policy class) is hard-wired to a
# concrete low-level class, EmailSenderBad. Switching to SMS or adding a
# new channel means editing NotificationServiceBad itself.

class EmailSenderBad:
    def send(self, message: str) -> str:
        return f"Email sent: {message}"


class NotificationServiceBad:
    def __init__(self):
        self.sender = EmailSenderBad()  # concrete dependency, hard-coded

    def notify(self, message: str) -> str:
        return self.sender.send(message)


# --- AFTER: follows DIP -------------------------------------------------------
#
# NotificationService depends only on the MessageSender abstraction.
# Concrete senders (Email, SMS, ...) are injected from the outside, so
# new channels can be added without touching NotificationService.

class MessageSender(ABC):
    @abstractmethod
    def send(self, message: str) -> str:
        raise NotImplementedError


class EmailSender(MessageSender):
    def send(self, message: str) -> str:
        return f"Email sent: {message}"


class SmsSender(MessageSender):
    def send(self, message: str) -> str:
        return f"SMS sent: {message}"


class NotificationService:
    def __init__(self, sender: MessageSender):
        self.sender = sender  # injected abstraction, not a concrete class

    def notify(self, message: str) -> str:
        return self.sender.send(message)


def demo_dip() -> None:
    section("DIP - Dependency Inversion Principle")

    print("-- BEFORE (violation): NotificationServiceBad is locked to EmailSenderBad --")
    bad_service = NotificationServiceBad()
    print(bad_service.notify("Order shipped"))

    print("\n-- AFTER (fixed): channel is injected via the MessageSender abstraction --")
    email_service = NotificationService(EmailSender())
    sms_service = NotificationService(SmsSender())
    print(email_service.notify("Order shipped"))
    print(sms_service.notify("Order shipped"))


# ---------------------------------------------------------------------------
# Entry point - run every demo in sequence.
# ---------------------------------------------------------------------------

def main() -> None:
    demo_srp()
    demo_ocp()
    demo_lsp()
    demo_isp()
    demo_dip()
    print("\n" + "=" * 70)
    print("All SOLID before/after demos ran successfully.")
    print("=" * 70)


if __name__ == "__main__":
    main()
