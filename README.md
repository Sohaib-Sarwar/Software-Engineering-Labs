# Database Systems Lab — E-Commerce Schema

Part of the **Software-Engineering-Labs** repository. This branch is scoped to a single subject — it contains only the `Database-Systems/` lab and this README; the `main` branch holds all subjects.

## What's here

A normalized (3NF) e-commerce schema (customers, products, orders, order_items) with sample data, labeled example queries (JOINs, aggregates, a subquery), a transaction example, and a Mermaid ER diagram.

```
Database-Systems/
├── schemas/
│   ├── schema.sql
│   └── er-diagram.md
├── sql/
│   ├── sample_data.sql
│   ├── queries.sql
│   └── transactions.sql
└── documentation/
    └── README.md
```

## Full write-up

See [`Database-Systems/documentation/README.md`](Database-Systems/documentation/README.md) for the schema design rationale and exact commands to load the database (SQLite) and run the example queries and transaction.
