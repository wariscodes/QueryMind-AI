CREATE DATABASE shop_sales_db;
USE shop_sales_db;

CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    price DECIMAL(10,2),
    stock INT
);

INSERT INTO products (product_name, category, price, stock)
VALUES
('Laptop', 'Electronics', 55000, 10),
('Smartphone', 'Electronics', 25000, 20),
('Headphones', 'Accessories', 2000, 50),
('Office Chair', 'Furniture', 7500, 15),
('Keyboard', 'Accessories', 1500, 30),
('Monitor', 'Electronics', 12000, 12),
('Desk', 'Furniture', 9000, 8),
('Mouse', 'Accessories', 800, 40);

CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(15),
    city VARCHAR(50),
    state VARCHAR(50),
    registration_date DATE
);

INSERT INTO customers
    (customer_name, email, phone, city, state, registration_date)
VALUES
    ('Rahul Sharma', 'rahul@example.com', '9876543210', 'Delhi', 'Delhi', '2025-01-15'),
    ('Priya Verma', 'priya@example.com', '9876543211', 'Jaipur', 'Rajasthan', '2025-02-20'),
    ('Amit Kumar', 'amit@example.com', '9876543212', 'Mumbai', 'Maharashtra', '2025-03-10'),
    ('Neha Singh', 'neha@example.com', '9876543213', 'Delhi', 'Delhi', '2025-04-05'),
    ('Rohan Gupta', 'rohan@example.com', '9876543214', 'Kota', 'Rajasthan', '2025-05-12'),
    ('Anjali Mehta', 'anjali@example.com', '9876543215', 'Jaipur', 'Rajasthan', '2025-06-18'),
    ('Vikas Yadav', 'vikas@example.com', '9876543216', 'Lucknow', 'Uttar Pradesh', '2025-07-22'),
    ('Simran Kaur', 'simran@example.com', '9876543217', 'Mumbai', 'Maharashtra', '2025-08-14'),
    ('Arjun Patel', 'arjun@example.com', '9876543218', 'Ahmedabad', 'Gujarat', '2025-09-09'),
    ('Pooja Jain', 'pooja@example.com', '9876543219', 'Kota', 'Rajasthan', '2025-10-25');
    
CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    order_date DATE NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(30),
    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);
INSERT INTO orders
    (customer_id, order_date, total_amount, status)
VALUES
    (1, '2026-01-10', 57000, 'Delivered'),
    (2, '2026-01-15', 25000, 'Delivered'),
    (1, '2026-02-05', 4000, 'Pending'),
    (3, '2026-02-12', 7500, 'Delivered'),
    (4, '2026-03-01', 12000, 'Cancelled'),
    (5, '2026-03-10', 9000, 'Delivered'),
    (6, '2026-04-02', 3000, 'Pending'),
    (2, '2026-04-15', 15000, 'Delivered'),
    (7, '2026-05-20', 55000, 'Delivered'),
    (8, '2026-06-11', 2000, 'Pending');
    
CREATE TABLE order_items (
    order_item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
INSERT INTO order_items
    (order_id, product_id, quantity, unit_price)
VALUES
    (1, 1, 1, 55000),
    (1, 3, 1, 2000),
    (2, 2, 1, 25000),
    (3, 5, 2, 1500),
    (4, 4, 1, 7500),
    (5, 6, 1, 12000),
    (6, 7, 1, 9000),
    (7, 3, 1, 2000),
    (8, 6, 1, 12000),
    (9, 1, 1, 55000),
    (10, 8, 2, 800);
SELECT
    o.order_id,
    c.customer_name,
    o.order_date,
    o.total_amount,
    o.status
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id;
UPDATE orders
SET total_amount = CASE order_id
    WHEN 3 THEN 3000.00
    WHEN 7 THEN 2000.00
    WHEN 8 THEN 12000.00
    WHEN 10 THEN 1600.00
    ELSE total_amount
END
WHERE order_id IN (3, 7, 8, 10);
SELECT
    o.order_id,
    o.total_amount AS order_total,
    SUM(oi.quantity * oi.unit_price) AS items_total
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
GROUP BY o.order_id, o.total_amount
ORDER BY o.order_id;

-- Best-selling products verify karna
SELECT
    p.product_name,
    SUM(oi.quantity) AS total_quantity_sold
FROM order_items oi
JOIN products p
    ON oi.product_id = p.product_id
JOIN orders o
    ON oi.order_id = o.order_id
WHERE o.status = 'Delivered'
GROUP BY p.product_id, p.product_name
ORDER BY total_quantity_sold DESC;

-- City-wise customer count
SELECT
    city,
    COUNT(*) AS total_customers
FROM customers
GROUP BY city
ORDER BY total_customers DESC;
SELECT * FROM products;
SELECT * FROM customers;
USE shop_sales_db;
SHOW TABLES;
SHOW TABLES;