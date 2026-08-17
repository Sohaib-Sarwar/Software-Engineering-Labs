# Database Systems Lab — E-Commerce Schema

A small, self-contained SQLite lab covering schema design, normalization,
joins, aggregation, subqueries, and transactions, built around a simple
e-commerce domain: customers place orders, orders contain line items, and
line items reference products.

## Folder layout

```
Database-Systems/
├── schemas/
│   ├── schema.sql        -- CREATE TABLE statements (customers, products, orders, order_items)
│   └── er-diagram.md     -- Mermaid ER diagram + normalization notes
├── sql/
│   ├── sample_data.sql   -- INSERT statements with realistic sample rows
│   ├── queries.sql       -- labeled example SELECT queries
│   └── transactions.sql  -- BEGIN/COMMIT/ROLLBACK transaction example
└── documentation/
    └── README.md         -- this file
```

## Schema design

Four tables, all in third normal form (see `schemas/er-diagram.md` for the
full reasoning):

| Table         | Purpose                                              | Primary key      | Foreign keys                                   |
|---------------|-------------------------------------------------------|------------------|-------------------------------------------------|
| `customers`   | People who can place orders                          | `customer_id`    | —                                                 |
| `products`    | Items available for sale, with price and stock level  | `product_id`     | —                                                 |
| `orders`      | One row per placed order ("header")                   | `order_id`       | `customer_id` → `customers.customer_id`          |
| `order_items` | One row per product line within an order ("detail")   | `order_item_id`  | `order_id` → `orders.order_id`, `product_id` → `products.product_id` |

Key constraints worth noting:

- `customers.email` and `products.sku` are `UNIQUE`, and `email` has a basic
  `CHECK` shape constraint.
- `products.unit_price` / `stock_quantity` and `order_items.quantity` /
  `unit_price` all have `CHECK` constraints preventing negative values.
- `orders.status` is constrained to a fixed set of values
  (`pending`, `processing`, `shipped`, `delivered`, `cancelled`).
- `order_items` has a `UNIQUE (order_id, product_id)` constraint, so a
  product appears at most once per order (increase `quantity` instead of
  inserting a duplicate line).
- `order_items.unit_price` intentionally stores the price *at the time of
  the order*, independent of `products.unit_price`, so historical invoices
  never change when a product's current price changes.
- Foreign keys use `ON DELETE RESTRICT` for `customers`/`products` (you
  cannot delete a customer or product that still has orders/order_items
  referencing it) and `ON DELETE CASCADE` from `orders` to `order_items`
  (deleting an order removes its line items).

## How to load the database

This lab targets [SQLite 3](https://sqlite.org/) via the `sqlite3` CLI
(bundled with most Linux/macOS installs; on Windows install it or use
`sqlite3.exe` from the official SQLite tools download, or run it through
Git Bash / WSL).

From the `Database-Systems/` directory:

```bash
# 1. Create the tables (drops and recreates them, so this is safe to re-run)
sqlite3 lab.db < schemas/schema.sql

# 2. Populate the tables with sample rows
sqlite3 lab.db < sql/sample_data.sql
```

This produces a `lab.db` file in the current directory containing the full
schema and sample data. `schema.sql` includes `PRAGMA foreign_keys = ON;`,
but that pragma applies per-connection — if you open `lab.db` separately in
your own script or the interactive shell, run it again first:

```bash
sqlite3 lab.db
sqlite> PRAGMA foreign_keys = ON;
```

## How to run the example queries

```bash
# Run every labeled query in one pass
sqlite3 -header -column lab.db < sql/queries.sql
```

`sql/queries.sql` contains six labeled, commented blocks:

1. **Basic SELECT / WHERE** — filter products by category and price.
2. **INNER JOIN** — a three-table join producing a per-line-item receipt.
3. **LEFT JOIN** — every customer with their order count and spend,
   including customers who have never ordered anything (the join keeps
   those rows instead of dropping them the way an INNER JOIN would).
4. **GROUP BY with HAVING** — total revenue per product category, filtered
   to categories above a revenue threshold.
5. **Subquery** — products that have never appeared in any order, found
   with a `NOT IN` subquery.
6. **Bonus: correlated subquery** — customers who spent more than the
   average customer's lifetime spend.

To run a single query while exploring interactively, open the file in an
editor, copy the block you want, and paste it into `sqlite3 lab.db`.

## How to run the transaction example

```bash
sqlite3 lab.db < sql/transactions.sql
```

`sql/transactions.sql` demonstrates:

- A successful `BEGIN TRANSACTION` → `UPDATE` stock → `INSERT` order →
  `INSERT` order_item → `COMMIT` sequence, using `last_insert_rowid()` to
  link the new `order_items` row to the `orders` row created earlier in the
  same transaction.
- A failed attempt (ordering far more units than are in stock) that ends in
  `ROLLBACK` instead, leaving stock and the order tables untouched.
- Commented guidance on when application code should `ROLLBACK` rather than
  `COMMIT` (failed preconditions, constraint violations, failed external
  validation, unexpected errors).
- A short explanation of SQLite's transaction/locking model versus the
  configurable isolation levels (READ COMMITTED, REPEATABLE READ,
  SERIALIZABLE) found in client/server databases like PostgreSQL or MySQL.

## Resetting the lab

`schema.sql` starts with `DROP TABLE IF EXISTS ...`, so to start over just
re-run both load steps:

```bash
sqlite3 lab.db < schemas/schema.sql
sqlite3 lab.db < sql/sample_data.sql
```

or simply delete `lab.db` and repeat the two load commands from scratch.
