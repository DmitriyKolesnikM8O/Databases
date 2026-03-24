er-diagram взята из лабы 1

## 1. Создание схемы базы данных

schema.sql - там DDL-скрипт.
Использую sqlite3, чтобы не замарачиваться.
Команды следующие:
- sqlite3 rental.db
- .read schema.sql
- .tables

## 2. Наполение базы данных

data.sql - там содержатся данные
- sqlite3 rental.db < data.sql
- .mode box (красивый вывод)
- SELECT * FROM users;
- SELECT * FROM equipment;

*Если не влезает в экран: .mode line*

## 3. Простые DML операции

прямо внутри sqlite вводил:

- вставка
```sql
INSERT INTO users (first_name, last_name, login, password_hash, phone, city) 
VALUES ('Алексей', 'Морозов', 'alex_snow', 'pass777', '+79110009988', 'Новосибирск');

INSERT INTO equipment (owner_id, category_id, name, description, price_per_day, total_quantity) 
VALUES (6, 1, 'Сноуборд Burton', 'Профессиональный борд, жесткость средняя', 2000.00, 2);
```

- обновление
```sql
UPDATE equipment 
SET price_per_day = 1450.00 
WHERE name = 'Велосипед GT Avalanche';

UPDATE rentals 
SET status = 'Завершен' 
WHERE id = 1;
```

- удаление
```sql
DELETE FROM reviews 
WHERE rating < 2;

DELETE FROM equipment 
WHERE name = 'Палатка 3-местная';
```


## 4. Запросы с агрегацией & 5. Запросы с соединениями таблиц

- сколько денег прошло через систему
```sql
SELECT SUM(payment_amount) AS total_revenue
FROM payments
WHERE status = 'Успешно';
```


- где у нас самое дорогое снаряжение, а где самое дешевое.
```sql
SELECT 
    c.name AS category_name, 
    AVG(e.price_per_day) AS avg_price,
    MIN(e.price_per_day) AS min_price,
    MAX(e.price_per_day) AS max_price
FROM equipment e
JOIN categories c ON e.category_id = c.id
GROUP BY c.name;
```

- какой вид спорта представлен шире всего
```sql
SELECT c.name AS category_name, COUNT(e.id) AS equipment_count
FROM categories c
LEFT JOIN equipment e ON c.id = e.category_id
GROUP BY c.name
ORDER BY equipment_count DESC;
```


- категории, где средняя цена аренды выше 1000 рублей
```sql
SELECT c.name, AVG(e.price_per_day) AS avg_price
FROM equipment e
JOIN categories c ON e.category_id = c.id
GROUP BY c.name
HAVING avg_price > 1000
ORDER BY avg_price DESC;
```

- посмотреть всех пользователей с их арендами
```sql
SELECT 
    u.first_name, 
    u.last_name, 
    u.city, 
    COUNT(r.id) AS total_rentals
FROM users u
LEFT JOIN rentals r ON u.id = r.renter_id
GROUP BY u.id;
```

- в каком городе больше всего денег приносит аренда
```sql
SELECT 
    u.city, 
    SUM(p.payment_amount) AS city_revenue
FROM users u
JOIN rentals r ON u.id = r.renter_id
JOIN payments p ON r.id = p.rental_id
WHERE p.status = 'Успешно'
GROUP BY u.city
ORDER BY city_revenue DESC;
```

## 6. Создание представлений
Чтобы увидеть все представления - .views
Обращаться, как к обычной таблице: select * from v_client_activity;

- общая картинка по пользователю: сколько раз арендовал, сколько денег принес, когда последний заказ
```sql
CREATE VIEW v_client_activity AS
SELECT 
    u.id AS user_id,
    u.first_name || ' ' || u.last_name AS full_name,
    u.city,
    COUNT(DISTINCT r.id) AS total_rentals,
    SUM(p.payment_amount) AS total_spent,
    MAX(r.start_date) AS last_rental_date
FROM users u
LEFT JOIN rentals r ON u.id = r.renter_id
LEFT JOIN payments p ON r.id = p.rental_id AND p.status = 'Успешно'
GROUP BY u.id;
```

- список товаров с владельцами, категориями, средними рейтингами
```sql
CREATE VIEW v_equipment_catalog AS
SELECT 
    e.id AS equipment_id,
    e.name AS equipment_name,
    c.name AS category_name,
    e.price_per_day,
    u.first_name || ' ' || u.last_name AS owner_name,
    ROUND(AVG(rev.rating), 1) AS avg_rating
FROM equipment e
JOIN categories c ON e.category_id = c.id
JOIN users u ON e.owner_id = u.id
LEFT JOIN reviews rev ON e.id = rev.equipment_id
GROUP BY e.id;
```

- детализация активных и завершенных аренд: кто что брал, когда и за сколько
```sql
CREATE VIEW v_rental_details AS
SELECT 
    r.id AS rental_id,
    u.first_name || ' ' || u.last_name AS customer_name,
    e.name AS item_name,
    r.start_date,
    r.end_date,
    ri.price_at_booking,
    r.status
FROM rentals r
JOIN users u ON r.renter_id = u.id
JOIN rental_items ri ON r.id = ri.rental_id
JOIN equipment e ON ri.equipment_id = e.id;
```


