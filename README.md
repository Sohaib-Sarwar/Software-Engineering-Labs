# Software Testing & QA — Lab

Part of the **Software-Engineering-Labs** repository. This branch is scoped to a single subject — it contains only the `Software-Testing/` lab and this README; the `main` branch holds all subjects.

## What's here

Unit tests for a small calculator module (covering equivalence partitioning & boundary value analysis), plus an integration test suite that exercises the Web-Engineering Notes API end-to-end over HTTP.

```
Software-Testing/
├── unit/
│   ├── calculator.py
│   └── test_calculator.py
├── integration/
│   └── test_notes_api_integration.py
└── documentation/
    └── README.md
```

Note: `integration/test_notes_api_integration.py` talks to the Notes API over HTTP, so it needs the Web-Engineering backend (`Web-Engineering/backend/app.py`, from the `main` or `Web-Engineering` branch) running locally first — it is not included on this branch.

## Full write-up

See [`Software-Testing/documentation/README.md`](Software-Testing/documentation/README.md) for the testing pyramid, the test case design technique used, and exact commands to run the unit and integration suites.
