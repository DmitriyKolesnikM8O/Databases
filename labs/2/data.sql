-- 1. категории
INSERT INTO categories (name, description) VALUES 
('Зимний спорт', 'Лыжи, сноуборды и аксессуары для зимы'),
('Велоспорт', 'Горные, городские и шоссейные велосипеды'),
('Кемпинг', 'Палатки, спальники и походное снаряжение');

-- 2. пользователи (владельцы и арендаторы)
INSERT INTO users (first_name, last_name, login, password_hash, phone, city) VALUES 
('Иван', 'Иванов', 'ivan_rent', 'hash123', '+79001112233', 'Москва'),
('Анна', 'Смирнова', 'anya_sport', 'hash456', '+79004445566', 'Санкт-Петербург'),
('Петр', 'Петров', 'pete_gear', 'hash789', '+79007778899', 'Москва'),
('Елена', 'Кузнецова', 'elena_pro', 'hash000', '+79001234567', 'Казань'),
('Дмитрий', 'Волков', 'dima_rent', 'hash111', '+79007654321', 'Москва');

-- 3. инвентарь
-- Иван (id=1) сдает лыжи и палатку
INSERT INTO equipment (owner_id, category_id, name, description, price_per_day, total_quantity) VALUES 
(1, 1, 'Лыжи Fischer', 'Горные лыжи для начинающих', 1500.00, 5),
(1, 3, 'Палатка 3-местная', 'Водостойкая палатка для походов', 800.00, 2);

-- Петр (id=3) сдает велосипеды
INSERT INTO equipment (owner_id, category_id, name, description, price_per_day, total_quantity) VALUES 
(3, 2, 'Велосипед GT Avalanche', 'Горный велосипед, 21 скорость', 1200.00, 3),
(3, 2, 'Шлем защитный', 'Размер L, высокая прочность', 300.00, 10);


-- 4. заказы аренды
-- Анна (id=2) берет лыжи в Москве на 3 дня
INSERT INTO rentals (renter_id, start_date, end_date, status) VALUES 
(2, '2024-01-10', '2024-01-13', 'Завершен');

-- Елена (id=4) берет велик и шлем на 2 дня
INSERT INTO rentals (renter_id, start_date, end_date, status) VALUES 
(4, '2024-05-20', '2024-05-22', 'Завершен');

-- 5. что именно взяли ( Rental_Items )
-- В первом заказе (id=1) была 1 пара лыж (id_equipment=1) по 1500 руб
INSERT INTO rental_items (rental_id, equipment_id, quantity, price_at_booking) VALUES 
(1, 1, 1, 1500.00);

-- Во втором заказе (id=2) был 1 велик (id=3) по 1200 руб и 1 шлем (id=4) по 300 руб
INSERT INTO rental_items (rental_id, equipment_id, quantity, price_at_booking) VALUES 
(2, 3, 1, 1200.00),
(2, 4, 1, 300.00);


-- 6. Платежи
-- Оплата за лыжи (1500 * 3 дня = 4500)
INSERT INTO payments (rental_id, payment_amount, payment_date, status) VALUES 
(1, 4500.00, '2024-01-10', 'Успешно');

-- Оплата за велик и шлем ((1200 + 300) * 2 дня = 3000)
INSERT INTO payments (rental_id, payment_amount, payment_date, status) VALUES 
(2, 3000.00, '2024-05-20', 'Успешно');

-- 7. Отзывы
INSERT INTO reviews (renter_id, equipment_id, rating, review_text) VALUES 
(2, 1, 5, 'Отличные лыжи, очень быстрые!'),
(4, 3, 4, 'Велосипед хороший, но скрипела цепь.');








