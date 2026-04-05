-- Очистим всё, если было
DROP TABLE IF EXISTS reviews, payments, rental_items, rentals, equipment, users, categories CASCADE;

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(256) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(256) NOT NULL,
    last_name VARCHAR(256),
    patronymic VARCHAR(256),
    login VARCHAR(256) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    city VARCHAR(100) NOT NULL
);

CREATE TABLE equipment (
    id SERIAL PRIMARY KEY,
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    name VARCHAR(256) NOT NULL,
    description TEXT,
    price_per_day NUMERIC(10, 2) NOT NULL, 
    total_quantity INTEGER NOT NULL CHECK (total_quantity >= 0) 
);

CREATE TABLE rentals (
    id SERIAL PRIMARY KEY,
    renter_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL,
    CHECK (end_date >= start_date) 
);

CREATE TABLE rental_items (
    rental_id INTEGER NOT NULL REFERENCES rentals(id) ON DELETE CASCADE,
    equipment_id INTEGER NOT NULL REFERENCES equipment(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price_at_booking NUMERIC(10, 2) NOT NULL,
    PRIMARY KEY (rental_id, equipment_id) 
);

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    rental_id INTEGER NOT NULL REFERENCES rentals(id) ON DELETE CASCADE,
    payment_amount NUMERIC(10, 2) NOT NULL CHECK (payment_amount > 0),
    payment_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL
);

CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    renter_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    equipment_id INTEGER NOT NULL REFERENCES equipment(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5), 
    review_text TEXT,
    created_at DATE NOT NULL DEFAULT CURRENT_DATE
);
