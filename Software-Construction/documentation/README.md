# Software Construction Lab

This folder contains self-contained, standard-library-only Python material
covering three core software construction topics:

1. Object-oriented programming (OOP) fundamentals, applied to a small
   library-management domain model.
2. Three classic design patterns: Singleton, Factory Method, and Observer.
3. Clean-code refactoring, contrasting a messy implementation with a
   refactored one.

Everything here runs with a plain Python 3 installation; no third-party
packages need to be installed.

## Folder structure

```
Software-Construction/
├── source/
│   ├── oop_library_system.py    # OOP domain model (encapsulation, inheritance, polymorphism)
│   ├── design_patterns.py       # Singleton, Factory Method, Observer
│   └── clean_code_refactor.py   # BEFORE (messy) vs AFTER (refactored) example
├── tests/
│   ├── test_oop_library_system.py
│   └── test_design_patterns.py
└── documentation/
    └── README.md                # this file
```

## Object-oriented programming principles

`source/oop_library_system.py` models a small lending library and is built
around the three pillars of OOP:

- **Encapsulation.** `Book` keeps its "copies currently on loan" counter as
  a name-mangled private attribute (`__copies_on_loan`). External code can
  only change it through `checkout_copy()` and `return_copy()`, which
  enforce the invariant `0 <= copies_on_loan <= total_copies`. This means a
  `Book` can never be pushed into an inconsistent state from outside the
  class.

- **Inheritance.** `Member` is an abstract base class (`abc.ABC`) that
  declares two abstract policy methods, `max_loans()` and
  `loan_period_days()`. Three concrete subclasses — `StandardMember`,
  `PremiumMember`, and `LibrarianMember` — each supply their own limits
  while reusing all of the shared bookkeeping logic (`_record_loan`,
  `_release_loan`, `active_loan_count`) defined once on the base class.

- **Polymorphism.** `LendingLibrary`, the manager class, is written
  entirely against the abstract `Member` interface. When it calls
  `member.max_loans()` or `member.loan_period_days()` during a checkout, it
  has no idea (and does not need to know) whether it is holding a
  `StandardMember`, a `PremiumMember`, or a `LibrarianMember` — the correct
  behaviour is selected automatically based on the object's actual runtime
  type. Adding a new member category in the future requires only a new
  subclass; `LendingLibrary` itself never has to change.

`LendingLibrary` is the invariant-enforcing manager class: it makes sure a
member never exceeds their personal loan limit, that a member can't borrow
the same title twice without returning it first, that a book cannot be
lent out with zero copies available, and that renewing an already-overdue
loan is refused. These are *cross-object* invariants (they depend on both
a `Book` and a `Member` at once), which is why they live in the manager
class rather than inside `Book` or `Member` individually.

## Design patterns

`source/design_patterns.py` implements three classic patterns. Run it
directly to see a short demo of each:

```bash
python source/design_patterns.py
```

### Singleton — `ConfigurationManager`

Guarantees that only one configuration object ever exists for the life of
the process, so different parts of an application can never disagree
about the current settings. It is implemented by overriding `__new__` to
return a cached instance, and by guarding `__init__` so repeated
construction does not reset already-initialized state. A
`_reset_for_testing()` class method is provided purely so unit tests can
start from a clean slate between test cases — production code should never
call it.

### Factory Method — `NotificationFactory`

`NotificationFactory` is an abstract creator that declares a
`create_notification()` factory method and a concrete `send()` template
method built on top of it. Three concrete factories
(`EmailNotificationFactory`, `SmsNotificationFactory`,
`PushNotificationFactory`) each decide which concrete `Notification`
product to instantiate. Client code (and the `send()` template method
itself) only ever talks to the abstract `Notification` interface — it
never names a concrete product class, so a brand-new notification channel
can be added later as a new factory/product pair with zero changes to any
existing code.

### Observer — `WeatherStation`

`WeatherStation` is the subject; any number of `Observer` implementations
(`CurrentConditionsDisplay`, `TemperatureAlertObserver`,
`MeasurementLogger`) can `attach()`/`detach()` themselves to it. When new
measurements arrive via `set_measurements()`, every attached observer is
notified through the same `update()` interface, without the station
knowing or caring what each observer does with the reading. This is the
standard pattern behind publish/subscribe UI updates, logging, and
alerting built on a single data source.

## Clean code practices

`source/clean_code_refactor.py` contains two versions of the same
behaviour — computing an order's subtotal, discounts, tax, shipping, and
receipt — placed one after another so they can be compared directly.

The `BEFORE` section (function `calc`) is deliberately left messy to
illustrate common problems:

- Cryptic, single-letter names (`o`, `t`, `i`, `p`, `q`, `s`, `tx`) that
  force a reader to trace the code just to learn what a variable holds.
- **Magic numbers** (`10`, `0.05`, `0.9`, `100`, `9.99`, `0.08`) with no
  explanation of what they mean or why those values were chosen.
- A single function doing calculation *and* console I/O, i.e. it has more
  than one reason to change and cannot be unit-tested without capturing
  stdout.
- A redundant `== True` boolean comparison and an untyped `dict` input.

The `AFTER` section refactors the same behaviour using:

- **Meaningful names** — `calculate_subtotal`, `apply_membership_discount`,
  `calculate_shipping_cost`, `OrderItem.unit_price`, and so on — so each
  identifier explains itself.
- **Named constants** instead of magic numbers — e.g.
  `BULK_DISCOUNT_MIN_QUANTITY`, `MEMBERSHIP_DISCOUNT_RATE`,
  `FREE_SHIPPING_MIN_SUBTOTAL` — documenting both the value and its
  business meaning in one place.
- **Small, single-responsibility functions** — each of
  `calculate_line_total`, `calculate_subtotal`,
  `apply_membership_discount`, `calculate_shipping_cost`,
  `calculate_tax`, and `summarize_order` does exactly one thing and can be
  tested independently with a plain equality assertion.
- **Separation of computation from I/O** — `summarize_order` and
  `format_receipt` are pure functions with no side effects; only
  `print_receipt` touches the console, isolating the one part of the code
  that is hard to unit test.

Run the module directly to see a sample receipt:

```bash
python source/clean_code_refactor.py
```

## Running the tests

Tests are written against the standard library's `unittest` module (no
`pytest` installation required), which also means they are automatically
discovered and run correctly if `pytest` happens to be available, since
pytest natively collects `unittest.TestCase` subclasses.

From the `Software-Construction/` directory, run:

```bash
python -m unittest discover tests
```

For more detail on which individual tests ran:

```bash
python -m unittest discover tests -v
```

To run a single test file directly:

```bash
python -m unittest tests.test_oop_library_system
python -m unittest tests.test_design_patterns
```

If `pytest` is installed, the same suite can also be run with:

```bash
pytest tests/
```

### What the tests cover

`tests/test_oop_library_system.py`:

- `Book` encapsulation: availability tracking, checkout/return, guarding
  against checking out a copy that doesn't exist and returning a copy that
  was never checked out.
- The `Member` hierarchy's polymorphic loan-limit behaviour across
  `StandardMember`, `PremiumMember`, and `LibrarianMember`.
- `LendingLibrary` invariants: checkout at capacity raises
  `LoanLimitExceededError`, checking out an unavailable book raises
  `BookNotAvailableError`, borrowing the same title twice raises an error,
  returning/renewing a loan that doesn't exist raises `LoanNotFoundError`,
  and renewing an already-overdue loan is refused.

`tests/test_design_patterns.py`:

- **Singleton**: repeated construction returns the *same* object identity,
  state set through one reference is visible through another, and
  resetting the singleton produces a genuinely new instance with default
  state restored.
- **Factory Method**: each concrete factory builds the correct concrete
  product type, the `send()` template method produces channel-specific
  output, and requesting an unknown channel raises `ValueError`.
- **Observer**: attaching the same observer twice does not duplicate
  notifications, all attached observers receive every update, detaching an
  observer stops future notifications (while it keeps its last known
  value), and the threshold-based alert observer only fires strictly above
  its threshold.
