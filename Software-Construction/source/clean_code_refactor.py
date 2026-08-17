"""
clean_code_refactor.py
=======================

This module pairs a deliberately messy implementation of an order-total
calculation (marked ``BEFORE``) with a refactored version of the exact same
behaviour (marked ``AFTER``), so the two can be read side by side.

The scenario: given a shopping order (a list of line items, a customer
name, and whether the customer is a paying member), compute the subtotal
(with a bulk-purchase discount and a membership discount), the shipping
cost, the sales tax, the grand total, and a printable receipt.

Read this file top to bottom -- the contrast is the point.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


# ===========================================================================
# BEFORE -- works, but is hard to read, test, and change safely.
# ===========================================================================
#
# Problems with the function below (kept intentionally, for teaching):
#
#   1. Cryptic single/double-letter names (``o``, ``t``, ``i``, ``p``, ``q``,
#      ``m``, ``s``, ``tx``, ``n``, ``c``) force the reader to hold the
#      meaning of every variable in their head instead of reading it off
#      the name.
#   2. Magic numbers (``10``, ``0.05``, ``0.9``, ``100``, ``9.99``,
#      ``0.08``) appear with no explanation of what they represent or why
#      those particular values were chosen.
#   3. It has more than one reason to change: it computes a subtotal,
#      applies two different discounts, computes shipping and tax, *and*
#      performs console I/O -- all in one function. A change to the receipt
#      wording risks breaking the math, and vice versa.
#   4. It is effectively untestable without capturing stdout, because the
#      calculation and the printing are not separated.
#   5. ``o['m'] == True`` is a redundant/error-prone boolean comparison,
#      and the untyped ``dict`` input gives no hints about what keys are
#      required.
#
def calc(o):
    t = 0
    for i in o['items']:
        t += i['p'] * i['q']
        if i['q'] > 10:
            t -= i['p'] * i['q'] * 0.05
    if o['m'] == True:
        t = t * 0.9
    if t > 100:
        s = 0
    else:
        s = 9.99
    tx = t * 0.08
    total = t + tx + s
    if o.get('c'):
        print("Receipt for " + o['n'])
        print("Subtotal: " + str(t))
        print("Tax: " + str(tx))
        print("Shipping: " + str(s))
        print("Total: " + str(total))
    return total


# ===========================================================================
# AFTER -- same behaviour, decomposed into small, well-named, single-
# responsibility pieces with named constants instead of magic numbers.
# ===========================================================================

# -- Named constants replace every magic number from the BEFORE version. ----
BULK_DISCOUNT_MIN_QUANTITY = 10       # units; strictly more than this qualifies
BULK_DISCOUNT_RATE = 0.05             # 5% off the line total for bulk lines
MEMBERSHIP_DISCOUNT_RATE = 0.10       # 10% off the whole subtotal for members
FREE_SHIPPING_MIN_SUBTOTAL = 100.0    # orders at/above this ship for free
STANDARD_SHIPPING_COST = 9.99
SALES_TAX_RATE = 0.08


@dataclass
class OrderItem:
    """A single line item: one product's unit price and quantity."""

    unit_price: float
    quantity: int

    def __post_init__(self) -> None:
        if self.unit_price < 0:
            raise ValueError("unit_price cannot be negative")
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")


@dataclass
class Order:
    """A customer order: who placed it, what is in it, and their membership status."""

    customer_name: str
    items: List[OrderItem]
    is_member: bool = False


@dataclass
class OrderSummary:
    """The computed monetary breakdown for an :class:`Order`."""

    subtotal: float
    tax: float
    shipping: float
    total: float


def calculate_line_total(item: OrderItem) -> float:
    """Return one line item's contribution to the subtotal, bulk discount applied."""
    line_total = item.unit_price * item.quantity
    if item.quantity > BULK_DISCOUNT_MIN_QUANTITY:
        line_total -= line_total * BULK_DISCOUNT_RATE
    return line_total


def calculate_subtotal(order: Order) -> float:
    """Sum every line item's discounted total for the whole order."""
    return sum(calculate_line_total(item) for item in order.items)


def apply_membership_discount(subtotal: float, is_member: bool) -> float:
    """Apply the flat membership discount to a subtotal, if applicable."""
    if not is_member:
        return subtotal
    return subtotal * (1 - MEMBERSHIP_DISCOUNT_RATE)


def calculate_shipping_cost(discounted_subtotal: float) -> float:
    """Orders at or above the free-shipping threshold ship for free."""
    if discounted_subtotal >= FREE_SHIPPING_MIN_SUBTOTAL:
        return 0.0
    return STANDARD_SHIPPING_COST


def calculate_tax(discounted_subtotal: float) -> float:
    """Sales tax is charged on the discounted subtotal only, not on shipping."""
    return discounted_subtotal * SALES_TAX_RATE


def summarize_order(order: Order) -> OrderSummary:
    """Compute the full monetary breakdown for an order.

    This function has one job: arithmetic. It performs no I/O, which makes
    it trivial to unit test with plain equality assertions.
    """
    subtotal = apply_membership_discount(calculate_subtotal(order), order.is_member)
    shipping = calculate_shipping_cost(subtotal)
    tax = calculate_tax(subtotal)
    total = subtotal + tax + shipping
    return OrderSummary(subtotal=subtotal, tax=tax, shipping=shipping, total=total)


def format_receipt(order: Order, summary: OrderSummary) -> str:
    """Render an order and its summary as a human-readable receipt string.

    Formatting is kept separate from calculation: changing the wording of
    the receipt can never introduce a math bug, and this function can be
    tested by comparing strings without touching stdout.
    """
    lines = [
        f"Receipt for {order.customer_name}",
        f"Subtotal: {summary.subtotal:.2f}",
        f"Tax: {summary.tax:.2f}",
        f"Shipping: {summary.shipping:.2f}",
        f"Total: {summary.total:.2f}",
    ]
    return "\n".join(lines)


def print_receipt(order: Order) -> OrderSummary:
    """Compute an order's summary and print its receipt.

    This is the only function in the AFTER section that performs I/O,
    isolating the side effect so the pure calculation functions above can
    be tested in isolation.
    """
    summary = summarize_order(order)
    print(format_receipt(order, summary))
    return summary


if __name__ == "__main__":
    sample_order = Order(
        customer_name="Priya Shah",
        items=[
            OrderItem(unit_price=12.50, quantity=3),
            OrderItem(unit_price=4.00, quantity=15),  # qualifies for bulk discount
        ],
        is_member=True,
    )
    print_receipt(sample_order)
