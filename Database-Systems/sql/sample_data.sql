-- ============================================================================
-- Database Systems Lab — Sample Data
-- File   : sql/sample_data.sql
-- Loaded after schemas/schema.sql. Populates all four tables with realistic
-- rows so the example queries in sql/queries.sql return meaningful results.
--
-- Notes on the data:
--   - Customers 7-10 intentionally have NO orders, so LEFT JOIN examples
--     have something interesting to demonstrate.
--   - Product "Standing Desk Converter" (product_id 12) is intentionally
--     never ordered, so the "products never ordered" subquery example
--     returns a non-empty result.
--   - order_items.unit_price is copied from the product's price at the time
--     the sample order was placed (see schema.sql for why this is stored).
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- customers (10 rows; 7-10 place no orders)
-- ----------------------------------------------------------------------------
INSERT INTO customers (first_name, last_name, email, phone, address_line1, address_line2, city, state, postal_code, country) VALUES
    ('John',   'Smith',     'john.smith@example.com',     '555-0101', '12 Elm Street',      NULL,        'Springfield', 'IL', '62701', 'USA'),
    ('Maria',  'Garcia',    'maria.garcia@example.com',   '555-0102', '48 Maple Avenue',    'Apt 3',     'Austin',      'TX', '73301', 'USA'),
    ('Wei',    'Chen',      'wei.chen@example.com',        '555-0103', '7 Birch Court',      NULL,        'Seattle',     'WA', '98101', 'USA'),
    ('Amara',  'Okafor',    'amara.okafor@example.com',    '555-0104', '221 Cedar Lane',     NULL,        'Atlanta',     'GA', '30301', 'USA'),
    ('Liam',   'O''Brien',  'liam.obrien@example.com',     '555-0105', '9 Willow Way',       'Unit 5',    'Boston',      'MA', '02101', 'USA'),
    ('Priya',  'Sharma',    'priya.sharma@example.com',    '555-0106', '360 Aspen Drive',    NULL,        'Denver',      'CO', '80201', 'USA'),
    ('Carlos', 'Rodriguez', 'carlos.rodriguez@example.com','555-0107', '15 Pine Street',     NULL,        'Miami',       'FL', '33101', 'USA'),
    ('Emma',   'Johnson',   'emma.johnson@example.com',    '555-0108', '82 Oakwood Blvd',    NULL,        'Chicago',     'IL', '60601', 'USA'),
    ('Yuki',   'Tanaka',    'yuki.tanaka@example.com',     '555-0109', '4 Sakura Court',     NULL,        'Portland',    'OR', '97201', 'USA'),
    ('Noah',   'Williams',  'noah.williams@example.com',   '555-0110', '129 Riverside Dr',   'Apt 12',    'Phoenix',     'AZ', '85001', 'USA');

-- ----------------------------------------------------------------------------
-- products (12 rows across three categories)
-- ----------------------------------------------------------------------------
INSERT INTO products (sku, product_name, description, category, unit_price, stock_quantity) VALUES
    ('SKU-1001', 'Wireless Mouse',              'Ergonomic 2.4GHz wireless mouse',            'Electronics', 19.99,  150),
    ('SKU-1002', 'Mechanical Keyboard',         'Tactile mechanical keyboard, brown switches', 'Electronics', 79.99,  80),
    ('SKU-1003', 'USB-C Hub',                   '7-in-1 USB-C hub with HDMI and card reader',  'Electronics', 34.50,  200),
    ('SKU-1004', '27" Monitor',                 '27-inch 1440p IPS monitor',                   'Electronics', 249.00, 40),
    ('SKU-1005', 'Laptop Stand',                'Adjustable aluminum laptop stand',            'Office',      29.95,  120),
    ('SKU-1006', 'Desk Lamp',                   'LED desk lamp with adjustable brightness',    'Office',      24.99,  90),
    ('SKU-1007', 'Notebook Set',                'Pack of 3 ruled notebooks',                   'Office',      9.99,   300),
    ('SKU-1008', 'Ballpoint Pen Pack',          'Pack of 12 ballpoint pens',                   'Office',      5.49,   500),
    ('SKU-1009', 'Noise Cancelling Headphones', 'Over-ear active noise cancelling headphones', 'Electronics', 199.99, 60),
    ('SKU-1010', 'Webcam 1080p',                'Full HD USB webcam with built-in microphone', 'Electronics', 45.00,  100),
    ('SKU-1011', 'Ergonomic Office Chair',      'Mesh-back office chair with lumbar support',  'Furniture',   189.99, 25),
    ('SKU-1012', 'Standing Desk Converter',     'Sit-stand desktop converter',                 'Furniture',   159.00, 35);

-- ----------------------------------------------------------------------------
-- orders (8 rows; customer_id 1-6 only, customers 7-10 have none)
-- ----------------------------------------------------------------------------
INSERT INTO orders (customer_id, order_date, status, shipping_address) VALUES
    (1, '2026-07-02 10:15:00', 'delivered',  '12 Elm Street, Springfield, IL 62701'),
    (2, '2026-07-05 14:42:00', 'delivered',  '48 Maple Avenue Apt 3, Austin, TX 73301'),
    (1, '2026-07-20 09:05:00', 'shipped',    '12 Elm Street, Springfield, IL 62701'),
    (3, '2026-07-22 16:30:00', 'delivered',  '7 Birch Court, Seattle, WA 98101'),
    (4, '2026-08-01 11:00:00', 'processing', '221 Cedar Lane, Atlanta, GA 30301'),
    (5, '2026-08-03 08:47:00', 'pending',    '9 Willow Way Unit 5, Boston, MA 02101'),
    (6, '2026-08-10 13:20:00', 'cancelled',  '360 Aspen Drive, Denver, CO 80201'),
    (2, '2026-08-15 17:55:00', 'pending',    '48 Maple Avenue Apt 3, Austin, TX 73301');

-- ----------------------------------------------------------------------------
-- order_items (line items for each order above)
-- ----------------------------------------------------------------------------
-- Order 1 (John Smith): mouse x2, keyboard x1
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (1, 1, 2, 19.99),
    (1, 2, 1, 79.99);

-- Order 2 (Maria Garcia): monitor x1, laptop stand x2
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (2, 4, 1, 249.00),
    (2, 5, 2, 29.95);

-- Order 3 (John Smith): headphones x1
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (3, 9, 1, 199.99);

-- Order 4 (Wei Chen): notebook set x5, pen pack x3, USB-C hub x1
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (4, 7, 5, 9.99),
    (4, 8, 3, 5.49),
    (4, 3, 1, 34.50);

-- Order 5 (Amara Okafor): office chair x1
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (5, 11, 1, 189.99);

-- Order 6 (Liam O'Brien): desk lamp x2, webcam x1
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (6, 6, 2, 24.99),
    (6, 10, 1, 45.00);

-- Order 7 (Priya Sharma, cancelled): keyboard x1
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (7, 2, 1, 79.99);

-- Order 8 (Maria Garcia): standing... no, desk converter not used here on
-- purpose so product 12 remains unordered; mouse x3 instead.
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (8, 1, 3, 19.99);
