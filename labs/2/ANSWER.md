er-diagram взята из лабы 1

## 1. Создание схемы базы данных

schema.sql - там DDL-скрипт.
Команды (шоб не забыть):
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

UPDATE equipment 
SET 
    price_per_day = price_per_day * 0.8,
    description = description || ' [ВЕСЕННЯЯ СКИДКА -20%]'
WHERE category_id = 1 
  AND total_quantity > 5
  AND owner_id IN (SELECT id FROM users WHERE city = 'Москва');



UPDATE equipment 
SET price_per_day = price_per_day + 500
WHERE id IN (
    SELECT equipment_id 
    FROM reviews 
    GROUP BY equipment_id 
    HAVING AVG(rating) > 4.5
);
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







### Запросы просто чтобы были

- список всех пользователей (имя, фамилию и телефон), которые живут в городе 'Москва'
```code
select first_name, last_name, phone from users where city='Москва';
```

- названия всех товаров (name) и их цену за день (price_per_day), отсортировав их от самых дорогих к самым дешевым
```code
select name, price_per_day as price from equipment order by price desc;
```

- в таблице инвентаря (equipment) все товары, в названии которых встречается слово 'Велосипед' 
```code
select name, description from equipment where name like 'Велосипед%';
```

- названия всех товаров (equipment.name) и рядом — название их категории (categories.name). Отсортируй результат по названию категории
```code
select e.name as equip_name, c.name as category_name from equipment as e join categories as c on e.category_id= c.id order by category_name;
```

- имя и фамилию владельца, а также название товара, который он сдает. Нас интересуют только те товары, цена которых больше 1000 рублей
```code
select u.first_name as owner_name, u.last_name as owner_surname, e.name as equip_name from users as u join equipment as e on e.owner_id=u.id where e.price_per_day > 1000;
```

- список всех аренд: ID аренды (rentals.id), дату начала (start_date) и логин пользователя, который совершил эту аренду
```code
select r.id, r.start_date, u.login from rentals as r join users as u on u.id=r.renter_id;
```

- имя, фамилию пользователя и количество (COUNT) товаров, которые он сдает в аренду. Не забудь сгруппировать результат по пользователю 
```code
select u.first_name as name, u.last_name as surname, count(e.name) as count_equip from users as u join equipment as e on e.owner_id=u.id group by u.id;
```

- В таблице payments лежат платежи. Выведи rental_id и общую сумму всех успешных платежей (SUM(payment_amount)) для каждого заказа. Отфильтруй только те платежи, где status = 'Успешно'.
```code
select r.id, sum(p.payment_amount) from rentals as r join payments as p on p.rental_id=r.id where p.status='Успешно' group by r.id;
```

- Для каждого товара в таблице reviews посчитай его средний рейтинг (AVG(rating)). Выведи название товара (equipment.name) и его среднюю оценку.
```code
select e.name, avg(r.rating) as equip_name from equipment as e join reviews as r on r.equipment_id=e.id group by e.name;
```

- Выведи названия категорий (categories.name), в которых больше 3 товаров.
```code
select c.name from categories as c join equipment as e on e.category_id=c.id group by c.name having count(e.name) > 3;
```

-  Выведи название одного самого дорогого товара (с максимальным price_per_day) во всей базе.
```code
SELECT name FROM equipment ORDER BY price_per_day DESC LIMIT 1;
```

- Выведи список всех аренд (ID аренды и даты), которые длились дольше 3 дней.
```code
SELECT id, start_date, end_date FROM rentals WHERE (julianday(end_date) - julianday(start_date)) > 3;
```

** Если условие можно проверить для одной строки (без суммы/среднего по группе) — используй WHERE. Это работает быстрее **

- Выведи имя и фамилию пользователей, которые потратили на аренду суммарно больше 5000 рублей.
```code
select u.first_name, u.last_name from users as u join rentals as r on r.renter_id=u.id join payments as p on p.rental_id=r.id group by u.id having sum(p.payment_amount) > 5000;
```

- Выведи имя владельца (users.first_name) и средний рейтинг всех его товаров.
```code
select u.first_name, avg(r.rating) from users as u left join equipment as e on e.owner_id=u.id left join reviews as r on r.equipment_id=e.id group by u.id;
```

- Выведи название категории и общую сумму стоимости всех товаров в этой категории (цена * количество).
```code
SELECT c.name, SUM(e.price_per_day * e.total_quantity) as category_value
FROM categories as c
JOIN equipment as e ON e.category_id = c.id
GROUP BY c.id;

```

- товары, которые ни раз ну арендовали
```code
SELECT e.id, e.name, c.name as category
FROM equipment e
JOIN categories c ON e.category_id = c.id
LEFT JOIN rental_items ri ON e.id = ri.equipment_id
WHERE ri.rental_id IS NULL;
```

- что берут чаще всего
```code
SELECT e.name, COUNT(ri.equipment_id) as rent_count
FROM equipment e
JOIN rental_items ri ON e.id = ri.equipment_id
GROUP BY e.id
ORDER BY rent_count DESC;
```

- Где кто зареган
```code
SELECT city, COUNT(*) as users_count
FROM users
GROUP BY city
ORDER BY users_count DESC;
```
