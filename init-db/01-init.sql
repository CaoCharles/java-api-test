-- 建立使用者資料表
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    full_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 建立產品資料表
CREATE TABLE IF NOT EXISTS products (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入測試資料
INSERT INTO users (username, email, full_name) VALUES
    ('john_doe', 'john@example.com', 'John Doe'),
    ('jane_smith', 'jane@example.com', 'Jane Smith'),
    ('bob_wilson', 'bob@example.com', 'Bob Wilson');

INSERT INTO products (name, description, price, stock) VALUES
    ('Laptop', 'High-performance laptop', 999.99, 50),
    ('Smartphone', 'Latest smartphone model', 699.99, 100),
    ('Headphones', 'Wireless noise-canceling headphones', 299.99, 200);
