-- ============================================================================
-- Database Systems Lab — E-Commerce Schema
-- Target engine : SQLite 3
-- File          : schemas/schema.sql
--
-- Purpose:
--   Defines a small, normalized (3NF) e-commerce database with four tables:
--     customers    - people who place orders
--     products     - items available for sale
--     orders       - one row per placed order (order "header")
--     order_items  - line items belonging to an order (order "detail")
--
-- Normalization summary (see schemas/er-diagram.md for the full discussion):
--   - Every non-key column depends on the whole primary key, and only on the
--     primary key (no partial or transitive dependencies) -> 3NF.
--   - orders / order_items resolves the many-to-many relationship between
--     customers+orders and products: a product can appear in many orders,
--     and an order can contain many products.
--   - order_items.unit_price intentionally stores the price AT THE TIME OF
--     THE ORDER. This is not redundant data — it is a historical fact of the
--     order line itself (product prices change over time; an old invoice
--     must not silently change when products.unit_price is updated later).
--
-- Load with:
--   sqlite3 lab.db < schemas/schema.sql
-- ============================================================================

PRAGMA foreign_keys = ON;

-- Drop tables in child-to-parent order so re-running this script is safe.
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

-- ----------------------------------------------------------------------------
-- customers
-- ----------------------------------------------------------------------------
CREATE TABLE customers (
    customer_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name      TEXT NOT NULL,
    last_name       TEXT NOT NULL,
    email           TEXT NOT NULL UNIQUE,
    phone           TEXT,
    address_line1   TEXT NOT NULL,
    address_line2   TEXT,
    city            TEXT NOT NULL,
    state           TEXT,
    postal_code     TEXT NOT NULL,
    country         TEXT NOT NULL DEFAULT 'USA',
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),

    CHECK (length(email) > 3 AND email LIKE '%_@_%')
);

-- ----------------------------------------------------------------------------
-- products
-- ----------------------------------------------------------------------------
CREATE TABLE products (
    product_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    sku             TEXT NOT NULL UNIQUE,
    product_name    TEXT NOT NULL,
    description     TEXT,
    category        TEXT NOT NULL,
    unit_price      NUMERIC NOT NULL CHECK (unit_price >= 0),
    stock_quantity  INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_products_category ON products (category);

-- ----------------------------------------------------------------------------
-- orders  (order "header": who placed it, when, and its current status)
-- ----------------------------------------------------------------------------
CREATE TABLE orders (
    order_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id         INTEGER NOT NULL,
    order_date          TEXT NOT NULL DEFAULT (datetime('now')),
    status              TEXT NOT NULL DEFAULT 'pending'
                            CHECK (status IN ('pending', 'processing', 'shipped',
                                               'delivered', 'cancelled')),
    shipping_address    TEXT NOT NULL,

    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE INDEX idx_orders_customer_id ON orders (customer_id);
CREATE INDEX idx_orders_order_date  ON orders (order_date);

-- ----------------------------------------------------------------------------
-- order_items  (order "detail": one row per product line within an order)
-- ----------------------------------------------------------------------------
CREATE TABLE order_items (
    order_item_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id        INTEGER NOT NULL,
    product_id      INTEGER NOT NULL,
    quantity        INTEGER NOT NULL CHECK (quantity > 0),
    unit_price      NUMERIC NOT NULL CHECK (unit_price >= 0),
        -- Price of the product AT THE MOMENT this line was ordered.
        -- Kept separate from products.unit_price on purpose (see header note).

    FOREIGN KEY (order_id) REFERENCES orders (order_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products (product_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    -- A given product should appear on at most one line per order; increase
    -- the quantity instead of adding a duplicate row.
    UNIQUE (order_id, product_id)
);

CREATE INDEX idx_order_items_order_id   ON order_items (order_id);
CREATE INDEX idx_order_items_product_id ON order_items (product_id);
