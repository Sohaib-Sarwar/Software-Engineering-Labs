-- ============================================================================
-- Database Systems Lab — Example Queries
-- File   : sql/queries.sql
-- Run after schema.sql and sample_data.sql have been loaded.
--
-- Each block below is self-contained and labeled with the SQL concept it
-- demonstrates. Run them individually, or the whole file at once with:
--   sqlite3 lab.db < sql/queries.sql
-- ============================================================================

PRAGMA foreign_keys = ON;


-- ============================================================================
-- Query 1: Basic SELECT with WHERE
-- Goal: list Electronics products priced under $50, cheapest first.
-- ============================================================================
SELECT
    product_name,
    category,
    unit_price,
    stock_quantity
FROM products
WHERE category = 'Electronics'
  AND unit_price < 50
ORDER BY unit_price ASC;


-- ============================================================================
-- Query 2: INNER JOIN across three tables
-- Goal: a line-item level receipt showing customer name, order id, product
-- name, quantity, and the historical unit price for every ordered item.
-- An INNER JOIN only returns rows that have a match in every joined table,
-- so orders/customers/products with no matching rows are excluded.
-- ============================================================================
SELECT
    o.order_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    p.product_name,
    oi.quantity,
    oi.unit_price,
    ROUND(oi.quantity * oi.unit_price, 2) AS line_total
FROM order_items AS oi
INNER JOIN orders    AS o ON oi.order_id   = o.order_id
INNER JOIN customers AS c ON o.customer_id = c.customer_id
INNER JOIN products   AS p ON oi.product_id = p.product_id
ORDER BY o.order_id, p.product_name;


-- ============================================================================
-- Query 3: LEFT JOIN
-- Goal: list every customer together with their order count and total spend,
-- INCLUDING customers who have never placed an order (customers 7-10 in the
-- sample data). A LEFT JOIN keeps every row from customers even when there
-- is no matching row in orders/order_items; the aggregate functions then
-- return 0/NULL for those customers instead of dropping them.
-- ============================================================================
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    COUNT(DISTINCT o.order_id) AS order_count,
    COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS lifetime_spend
FROM customers AS c
LEFT JOIN orders      AS o  ON c.customer_id = o.customer_id
LEFT JOIN order_items AS oi ON o.order_id    = oi.order_id
GROUP BY c.customer_id, customer_name
ORDER BY lifetime_spend DESC;


-- ============================================================================
-- Query 4: Aggregate GROUP BY with HAVING
-- Goal: total revenue per product category, restricted to categories whose
-- combined revenue exceeds $150. HAVING filters on the aggregated value
-- (SUM), which WHERE cannot do because WHERE runs before grouping.
-- ============================================================================
SELECT
    p.category,
    COUNT(oi.order_item_id) AS items_sold,
    SUM(oi.quantity)                     AS units_sold,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS category_revenue
FROM order_items AS oi
INNER JOIN products AS p ON oi.product_id = p.product_id
GROUP BY p.category
HAVING SUM(oi.quantity * oi.unit_price) > 150
ORDER BY category_revenue DESC;


-- ============================================================================
-- Query 5: Subquery
-- Goal: find every product that has never appeared in an order_items row,
-- using a NOT IN subquery over the distinct product_ids that were ordered.
-- (In the sample data this returns "Standing Desk Converter" only.)
-- ============================================================================
SELECT
    product_id,
    product_name,
    category,
    unit_price,
    stock_quantity
FROM products
WHERE product_id NOT IN (
    SELECT DISTINCT product_id
    FROM order_items
)
ORDER BY product_name;


-- ============================================================================
-- Bonus Query 6: Correlated subquery
-- Goal: list customers whose lifetime spend is above the average lifetime
-- spend across all customers who have placed at least one order.
-- ============================================================================
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS lifetime_spend
FROM customers AS c
INNER JOIN orders      AS o  ON c.customer_id = o.customer_id
INNER JOIN order_items AS oi ON o.order_id    = oi.order_id
GROUP BY c.customer_id, customer_name
HAVING SUM(oi.quantity * oi.unit_price) > (
    SELECT AVG(customer_total)
    FROM (
        SELECT SUM(oi2.quantity * oi2.unit_price) AS customer_total
        FROM orders AS o2
        INNER JOIN order_items AS oi2 ON o2.order_id = oi2.order_id
        GROUP BY o2.customer_id
    )
)
ORDER BY lifetime_spend DESC;
