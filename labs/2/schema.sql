PRAGMA foreign_keys = ON;

CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(256) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(256) NOT NULL,
    last_name VARCHAR(256),
    patronymic VARCHAR(256),
    login VARCHAR(256) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    city VARCHAR(100) NOT NULL
);

CREATE TABLE equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    name VARCHAR(256) NOT NULL,
    description TEXT,
    price_per_day NUMERIC(10, 2) NOT NULL, 
    total_quantity INTEGER NOT NULL CHECK (total_quantity >= 0),
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
);

CREATE TABLE rentals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    renter_id INTEGER NOT NULL,
    start_date TEXT NOT NULL, 
    end_date TEXT NOT NULL,
    status VARCHAR(50) NOT NULL,
    CHECK (end_date >= start_date),
    FOREIGN KEY (renter_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE rental_items (
    rental_id INTEGER NOT NULL,
    equipment_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price_at_booking NUMERIC(10, 2) NOT NULL,
    PRIMARY KEY (rental_id, equipment_id),
    FOREIGN KEY (rental_id) REFERENCES rentals(id) ON DELETE CASCADE,
    FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE CASCADE
);

CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rental_id INTEGER NOT NULL,
    payment_amount NUMERIC(10, 2) NOT NULL CHECK (payment_amount > 0),
    payment_date TEXT NOT NULL,
    status VARCHAR(50) NOT NULL,
    FOREIGN KEY (rental_id) REFERENCES rentals(id) ON DELETE CASCADE
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    renter_id INTEGER NOT NULL,
    equipment_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    created_at TEXT NOT NULL DEFAULT (date('now')),
    FOREIGN KEY (renter_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE CASCADE
);
