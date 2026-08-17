# Software Testing & QA - Lab Notes

This folder is a small, self-contained lab on software testing concepts and
practice. It contains a real (tiny) codebase, a full unit test suite for it,
and an integration test suite written against the separate `Web-Engineering`
Notes API, so you can see unit testing and integration testing side by side
and understand exactly what distinguishes them.

```
Software-Testing/
  unit/
    calculator.py                    - module under test
    test_calculator.py               - unit tests for calculator.py
    __init__.py                      - (empty) makes "unit" importable as a package
  integration/
    test_notes_api_integration.py    - integration tests for the Notes REST API
    __init__.py                      - (empty) makes "integration" importable as a package
  documentation/
    README.md                        - this file
```

---

## 1. The testing pyramid

The "testing pyramid" is a mental model for how much of each kind of test a
healthy project should have. Read from the bottom (most tests, cheapest,
fastest) to the top (fewest tests, most expensive, slowest):

```
                /\
               /  \        System / End-to-End tests
              /----\       (whole application, real environment)
             /      \
            / Integ- \     Integration tests
           /  ration  \    (several units working together, e.g. an API + its
          /------------\    HTTP layer, or code talking to a real database)
         /              \
        /      Unit      \  Unit tests
       /       tests      \ (one function / one class, in isolation)
      /--------------------\
```

### Unit testing

A **unit test** exercises the smallest testable piece of code - usually a
single function or method - in complete isolation from everything else
(no network, no database, no filesystem, no other modules' behavior mixed
in). Unit tests are:

- **Fast** - thousands can run in well under a second, because there is no
  I/O.
- **Deterministic** - the same input always produces the same output, so
  there's nothing flaky to chase.
- **Precise** - when one fails, you know exactly which function broke,
  because nothing else was involved.

`unit/test_calculator.py` is a pure unit test suite: it imports
`calculator.py` directly as a Python module and calls its functions with
various inputs. There is no server, no network call, nothing external - just
the function and the assertion.

### Integration testing

An **integration test** exercises two or more units *together*, checking
that they cooperate correctly - for example, that an HTTP layer correctly
parses a request, calls the right business logic, and serializes the right
response, all the way through a real (if small) running system. Integration
tests are:

- **Slower** than unit tests (they involve real I/O: sockets, disk, or a
  database).
- **More realistic** - they catch bugs that only show up when pieces are
  wired together (wrong HTTP status code, wrong JSON shape, a header that
  never gets attached, a route that isn't registered, etc.) which pure unit
  tests, run against isolated functions, cannot catch.
- **More fragile / environment-dependent** - they need something else to be
  running (in this case, the Flask backend), and can fail for reasons that
  have nothing to do with a logic bug (server not started, wrong port,
  network hiccup).

`integration/test_notes_api_integration.py` is an integration test suite: it
sends real HTTP requests over a real socket to a real running instance of
the `Web-Engineering` Notes API (`../Web-Engineering/backend/app.py`) and
checks the actual HTTP status codes and JSON bodies that come back. It does
**not** import any of that server's Python code directly - it only talks to
it the way a real client (a browser, a mobile app, `curl`) would: over HTTP.

### System, functional, and regression testing (where they fit above the pyramid)

These sit above integration tests because they test even larger scopes,
usually the whole assembled application:

- **System testing** verifies the *complete, integrated application* -
  frontend, backend, and any infrastructure - end to end, exactly as a real
  deployment would run. For this lab's sibling project, that would mean
  opening the Notes frontend in a browser, logging in, and creating a note
  through the actual UI, with the actual backend running behind it.
- **Functional testing** verifies specific *features from the user's point
  of view*, against requirements ("can a logged-in user delete a note they
  created?"), rather than against internal code structure. It can be done at
  the system level (through the UI) or the API level (through HTTP, like our
  integration tests do here) - the distinguishing trait is that it's judged
  against a requirement/behavior, not an implementation detail.
- **Regression testing** is not a distinct test *level* so much as a
  *purpose*: re-running an existing suite of tests (unit, integration,
  and/or system) after a change, specifically to catch cases where a fix or
  a new feature accidentally broke something that used to work. Every test
  in this lab doubles as a regression test the moment it's added: run it
  again after your next change, and it's protecting you from regressions.

**Why the pyramid shape matters:** unit tests are cheap, so you should have
many of them, covering every function and every edge case, as
`test_calculator.py` does for each of the five calculator operations.
Integration and system tests are valuable but expensive and slower, so you
write fewer of them, aimed at the seams between components and the
highest-value user flows - which is exactly what
`test_notes_api_integration.py` does: it doesn't re-test every possible
input to `_validate_note_payload()` (the unit-level concern of the backend
itself), it tests that each *endpoint*, as a whole, does the right thing
over HTTP (right status code, right auth behavior, right JSON shape).

---

## 2. Test case design technique: equivalence partitioning & boundary value analysis

Writing "a few tests that feel right" tends to under-test some inputs and
over-test others. Two systematic techniques used throughout
`test_calculator.py` fix that:

### Equivalence partitioning (EP)

Split all possible inputs to a function into **partitions** (groups) where,
if the function behaves correctly for *one* value in the group, it's
reasonable to expect it behaves correctly for *every* value in that group.
Then pick just one (or a couple of) representative value(s) per partition,
instead of testing every possible input.

### Boundary value analysis (BVA)

Bugs cluster at the **edges** of partitions far more often than in the
middle of them (off-by-one errors, `<` vs `<=`, forgetting a special case
at zero). BVA says: in addition to EP, specifically test the values sitting
exactly on - and just next to - the boundary between two partitions.

### Concrete worked example, from `calculator.py`: `divide(a, b)`

For the divisor `b`, there are two equivalence partitions:

| Partition            | Representative example | Expected behavior            |
|-----------------------|-------------------------|-------------------------------|
| `b` is any non-zero number (positive or negative) | `b = 2`, `b = -2` | returns `a / b` |
| `b == 0` (the boundary case) | `b = 0` | raises `ZeroDivisionError` |

`b == 0` is simultaneously its *own* equivalence partition **and** the
boundary value between "divisor is negative" and "divisor is positive" - the
single riskiest input to this function, which is exactly why it gets
dedicated test cases in `test_calculator.py`:

```python
def test_divide_by_zero_raises_zero_division_error(self):
    # This is the critical boundary case for this module: b == 0.
    with self.assertRaises(ZeroDivisionError) as ctx:
        divide(10, 0)
    self.assertIn("division by zero", str(ctx.exception))

def test_divide_by_zero_with_zero_numerator_still_raises(self):
    # 0 / 0 is undefined too - must still raise, not return NaN.
    with self.assertRaises(ZeroDivisionError):
        divide(0, 0)
```

alongside representative, non-boundary tests for the "normal" partition:

```python
def test_normal_division(self):
    self.assertEqual(divide(10, 2), 5)

def test_division_with_negative_numbers(self):
    self.assertEqual(divide(-10, 2), -5)
    self.assertEqual(divide(10, -2), -5)
    self.assertEqual(divide(-10, -2), 5)
```

The same technique is applied to `power(base, exponent)`, which has an even
sharper boundary: `base == 0` combines with the sign of `exponent` to create
three partitions (`exponent > 0` -> `0`, `exponent == 0` -> `1` by
convention, `exponent < 0` -> `ZeroDivisionError`), each covered by its own
test in `TestPower`.

Applying EP + BVA consistently is *why* `test_calculator.py` has roughly
5-10 test methods per function instead of one "happy path" test each: each
method targets one identified partition or boundary, not an arbitrary guess.

---

## 3. Running the tests

All tests use only Python's standard library (`unittest`, `urllib`) - no
`pip install` is required to run the unit tests.

### Run everything (unit + integration) with test discovery

From inside this `Software-Testing/` folder:

```bash
python -m unittest discover
```

Add `-v` for verbose, per-test output:

```bash
python -m unittest discover -v
```

`unittest discover` walks this folder, finds every `test_*.py` file in
`unit/` and `integration/`, and runs them together as one suite.

### Run just the unit tests

```bash
python -m unittest discover -s unit -v
```

These never touch the network and will always run (no setup required).

### Run just the integration tests

**The backend server must be running first.** The integration suite talks
to the Notes API over real HTTP, so start it in a separate terminal before
running these tests:

```bash
cd ../Web-Engineering/backend
pip install flask      # only needed the first time
python app.py
```

Leave that running (it listens on `http://127.0.0.1:5000` by default), then
in another terminal, from this `Software-Testing/` folder:

```bash
python -m unittest integration.test_notes_api_integration -v
```

If you run `python -m unittest discover` (or run the integration file)
**without** starting the backend first, the integration tests will report
themselves as **SKIPPED** (not failed) with a message telling you exactly
how to start the server - `python -m unittest discover` will still finish
cleanly either way, since the unit tests never depend on the server.

### Run a single test file directly

```bash
python -m unittest unit/test_calculator.py -v
```

or, from inside `unit/`:

```bash
python test_calculator.py -v
```
