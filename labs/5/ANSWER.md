# Лабораторная работа №5: Исследование транзакций в PostgreSQL

## Сценарий 1: Новая аренда

Создание нового заказа на аренду включает:
1. Создание записи в `rentals`
2. Добавление товаров в `rental_items`
3. Создание записи об оплате в `payments`

---

### 1.1 Успешное выполнение транзакции (COMMIT)

```sql
BEGIN;

-- Шаг 1: Создаем новую аренду
INSERT INTO rentals (renter_id, start_date, end_date, status)
VALUES (100, '2024-12-01', '2024-12-05', 'Новый');

-- Шаг 2: Добавляем товары в аренду
INSERT INTO rental_items (rental_id, equipment_id, quantity, price_at_booking)
VALUES 
    (currval('rentals_id_seq'), 50, 2, 1500.00),
    (currval('rentals_id_seq'), 100, 1, 800.00);

-- Шаг 3: Регистрируем оплату
INSERT INTO payments (rental_id, payment_amount, payment_date, status)
VALUES (currval('rentals_id_seq'), 3800.00, '2024-12-01', 'Успешно');

-- Фиксация изменений
COMMIT;
```

**Результат:** Все три таблицы обновлены атомарно.

---

### 1.2 Ошибка внутри транзакции (полный откат — ROLLBACK)

```sql
BEGIN;

-- Шаг 1: Создаем новую аренду
INSERT INTO rentals (renter_id, start_date, end_date, status)
VALUES (100, '2024-12-01', '2024-12-05', 'Новый');

-- Шаг 2: Добавляем товары в аренду
INSERT INTO rental_items (rental_id, equipment_id, quantity, price_at_booking)
VALUES 
    (currval('rentals_id_seq'), 50, 2, 1500.00),
    (currval('rentals_id_seq'), 999999, 1, 800.00);  -- ОШИБКА: equipment_id=999999 не существует

-- Шаг 3: Регистрируем оплату (не выполнится из-за ошибки)
INSERT INTO payments (rental_id, payment_amount, payment_date, status)
VALUES (currval('rentals_id_seq'), 3800.00, '2024-12-01', 'Успешно');

COMMIT;
```

**Результат:** Ошибка! Всё откатывается.

```
ERROR: insert or update on table "rental_items" violates foreign key constraint "rental_items_equipment_id_fkey"
DETAIL: Key (equipment_id)=(999999) is not present in table "equipment".
ROLLBACK
```

**Проверка:** Данных в таблицах нет — полный откат.

---

### 1.3 Точка сохранения (частичный откат — SAVEPOINT)

```sql
BEGIN;

-- Шаг 1: Создаем новую аренду
INSERT INTO rentals (renter_id, start_date, end_date, status)
VALUES (100, '2024-12-01', '2024-12-05', 'Новый');

-- Точка сохранения после создания заказа
SAVEPOINT sp1;

-- Шаг 2: Пытаемся добавить первый товар
INSERT INTO rental_items (rental_id, equipment_id, quantity, price_at_booking)
VALUES (currval('rentals_id_seq'), 50, 2, 1500.00);

-- Точка сохранения после первого товара
SAVEPOINT sp2;

-- Шаг 3: Пытаемся добавить НЕСУЩЕСТВУЮЩИЙ товар (ошибка)
INSERT INTO rental_items (rental_id, equipment_id, quantity, price_at_booking)
VALUES (currval('rentals_id_seq'), 999999, 1, 800.00);  -- ОШИБКА!

-- Если бы не было ошибки, дошли бы до сюда и закоммитили бы
-- Но случилась ошибка, откатываемся к точке sp2
ROLLBACK TO SAVEPOINT sp2;

-- Продолжаем работу - добавляем другой товар
INSERT INTO rental_items (rental_id, equipment_id, quantity, price_at_booking)
VALUES (currval('rentals_id_seq'), 75, 1, 1200.00);

-- Шаг 4: Оплата
INSERT INTO payments (rental_id, payment_amount, payment_date, status)
VALUES (currval('rentals_id_seq'), 4200.00, '2024-12-01', 'Успешно');

COMMIT;
```

**Результат:** Первый товар (id=50) добавлен, второй с ошибкой пропущен, третий (id=75) добавлен. Аренда и оплата созданы.

---

## Сценарий 2: Обновление стока при завершении аренды

При завершении аренды нужно:
1. Изменить статус аренды на "Завершен"
2. Вернуть количество товаров обратно в equipment

---

### 2.1 Успешное выполнение

```sql
BEGIN;

-- Находим аренду и её товары
-- Предполагаем, что аренда id=5 содержит товар equipment_id=10 в количестве 2

-- Шаг 1: Возвращаем товар на склад (увеличиваем количество)
UPDATE equipment 
SET total_quantity = total_quantity + 2 
WHERE id = 10;

-- Шаг 2: Завершаем аренду
UPDATE rentals 
SET status = 'Завершен' 
WHERE id = 5;

COMMIT;
```

---

### 2.2 Ошибка и полный откат

```sql
BEGIN;

-- Шаг 1: Возвращаем товар на склад
UPDATE equipment 
SET total_quantity = total_quantity + 2 
WHERE id = 10;

-- Шаг 2: Пытаемся завершить несуществующую аренду
UPDATE rentals 
SET status = 'Завершен' 
WHERE id = 999999;  -- ОШИБКА: нет такой аренды

COMMIT;
```

**Результат:** Ошибка, изменения в equipment откатываются.

---

### 2.3 Частичный откат через SAVEPOINT

```sql
BEGIN;

SAVEPOINT sp_start;

-- Шаг 1: Возвращаем первый товар
UPDATE equipment 
SET total_quantity = total_quantity + 2 
WHERE id = 10;

SAVEPOINT sp_first_item;

-- Шаг 2: Пытаемся вернуть второй товар (несуществующий)
UPDATE equipment 
SET total_quantity = total_quantity + 5 
WHERE id = 999999;  -- ОШИБКА

ROLLBACK TO SAVEPOINT sp_first_item;

-- Шаг 3: Возвращаем другой товар
UPDATE equipment 
SET total_quantity = total_quantity + 3 
WHERE id = 20;

-- Шаг 4: Завершаем аренду
UPDATE rentals 
SET status = 'Завершен' 
WHERE id = 5;

COMMIT;
```

---

## Сценарий 3: Регистрация + размещение оборудования

Новый пользователь регистрируется и сразу размещает оборудование для аренды.

---

### 3.1 Успешное выполнение

```sql
BEGIN;

-- Шаг 1: Регистрируем нового пользователя
INSERT INTO users (first_name, last_name, login, password_hash, phone, city)
VALUES ('Новый', 'Пользователь', 'new_user_123', 'hash_abc', '+79001234567', 'Москва');

-- Получаем ID нового пользователя
-- Шаг 2: Добавляем его оборудование
INSERT INTO equipment (owner_id, category_id, name, description, price_per_day, total_quantity)
VALUES 
    (currval('users_id_seq'), 1, 'Горные лыги', 'Профессиональные лыжи', 2000.00, 3),
    (currval('users_id_seq'), 2, 'Велосипед', 'Городской велосипед', 1500.00, 2);

COMMIT;
```

---

### 3.2 Ошибка — полный откат

```sql
BEGIN;

-- Шаг 1: Регистрируем пользователя
INSERT INTO users (first_name, last_name, login, password_hash, phone, city)
VALUES ('Тест', 'Тестов', 'test_user', 'hash_xyz', '+79001112233', 'СПб');

-- Шаг 2: Пытаемся добавить оборудование с НЕСУЩЕСТВУЮЩЕЙ категорией
INSERT INTO equipment (owner_id, category_id, name, description, price_per_day, total_quantity)
VALUES (currval('users_id_seq'), 999, 'Товар', 'Описание', 1000.00, 1);  -- ОШИБКА

COMMIT;
```

**Результат:** Пользователь не будет создан.

---

### 3.3 Частичный откат

```sql
BEGIN;

SAVEPOINT sp_user;

-- Шаг 1: Создаем первого пользователя
INSERT INTO users (first_name, last_name, login, password_hash, phone, city)
VALUES ('Первый', 'Пользователь', 'user_one', 'hash1', '+79001112233', 'Москва');

SAVEPOINT sp_first_user;

-- Шаг 2: Создаем второго пользователя с дублирующимся phone (ошибка!)
INSERT INTO users (first_name, last_name, login, password_hash, phone, city)
VALUES ('Второй', 'Пользователь', 'user_two', 'hash2', '+79001112233', 'Казань');  -- ОШИБКА: phone уже существует

ROLLBACK TO SAVEPOINT sp_first_user;

-- Продолжаем с первым пользователем
-- Шаг 3: Добавляем оборудование для первого пользователя
INSERT INTO equipment (owner_id, category_id, name, description, price_per_day, total_quantity)
VALUES (currval('users_id_seq'), 1, 'Лыжи', 'Для профи', 2500.00, 2);

COMMIT;
```

---

## Сценарий 4 (Дополнительный): Параллельное выполнение транзакций

### 4.1 Блокировка данных (Row Level Lock)

**Тест:**

1. **Сессия 1:** Начальная цена оборудования id=10:
```sql
SELECT price_per_day FROM equipment WHERE id = 10;
-- Результат: 110.00
```

2. **Сессия 1:** Начинает транзакцию и обновляет цену:
```sql
BEGIN;
UPDATE equipment SET price_per_day = 5000 WHERE id = 10;
-- Блокировка строки установлена
```

3. **Сессия 2:** Пытается обновить ту же строку:
```sql
BEGIN;
UPDATE equipment SET price_per_day = 6000 WHERE id = 10;
-- Блокировка! Сессия 2 ждёт...
```

4. **Сессия 1:** Фиксирует изменения:
```sql
COMMIT;
-- Блокировка снята
```

5. **Сессия 2:** Продолжает выполнение (после ожидания):
```sql
COMMIT;
-- Применяет своё изменение
```

6. **Проверка:**
```sql
SELECT price_per_day FROM equipment WHERE id = 10;
-- Результат: 6000.00 (последнее значение выиграло)
```

**Вывод:** PostgreSQL использует построчную блокировку (row-level lock). Вторая транзакция ждёт, пока первая не завершится (COMMIT или ROLLBACK).

---

### 4.2 Уровни изоляции — Фантомное чтение

#### Тест 1: READ COMMITTED (по умолчанию)

```sql
-- Сессия 1: Уровень READ COMMITTED
BEGIN;
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;


-- Первый подсчёт
SELECT COUNT(*) FROM equipment WHERE category_id = 1;
-- Результат: X (текущее количество)

-- (В это время Сессия 2 добавляет новую запись с category_id = 1 и COMMIT:
	 BEGIN;
	 INSERT INTO equipment (owner_id, category_id, name, description, price_per_day, total_quantity)
	 VALUES (16, 1, 'Тестовая лыжа для фантома', 'Для параллельного теста', 1500.00, 1);)

-- Второй подсчёт в той же транзакции
SELECT COUNT(*) FROM equipment WHERE category_id = 1;
-- Результат: X+1 (ВИДИМ НОВУЮ запись!)

COMMIT;
```

**Результат:** Количество изменилось — **фантомное чтение присутствует** на уровне READ COMMITTED.

---

#### Тест 2: REPEATABLE READ

```sql
-- Сессия 1: Уровень REPEATABLE READ
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;


-- Первый подсчёт
SELECT COUNT(*) FROM equipment WHERE category_id = 1;
-- Результат: X (зафиксирован в snapshot'е)

-- (В это время Сессия 2 добавляет новую запись с category_id = 1 и COMMIT)

-- Второй подсчёт в той же транзакции
SELECT COUNT(*) FROM equipment WHERE category_id = 1;
-- Результат: X (НЕ ВИДИМ новую запись!)

COMMIT;
```

**Результат:** Количество НЕ изменилось — **фантомное чтение отсутствует** на уровне REPEATABLE READ.

---

### 4.3 Аномалия "Потерянное обновление" (Lost Update)

**Сценарий:** Два пользователя одновременно читают и обновляют одну и ту же строку.

```sql
-- Начальное значение: price_per_day = 6000

-- Сессия 1:
BEGIN;
SELECT price_per_day FROM equipment WHERE id = 10;
-- Видит: 6000

-- Сессия 2 (параллельно):
BEGIN;
SELECT price_per_day FROM equipment WHERE id = 10;
-- Видит: 6000
UPDATE equipment SET price_per_day = 6500 WHERE id = 10;
COMMIT;

-- Сессия 1:
UPDATE equipment SET price_per_day = 7000 WHERE id = 10;
COMMIT;

-- Результат в базе: 7000
-- Обновление сессии 2 (до 6500) БЫЛО ПОТЕРЯНО!
```

**Вывод:** На уровне READ COMMITTED возможна аномалия "потерянное обновление". Для её избежания нужно использовать REPEATABLE READ или SERIALIZABLE.

---

### 4.4 Уровень SERIALIZABLE

На уровне SERIALIZABLE PostgreSQL проверяет возможные конфликты и может выдать ошибку:

```sql
BEGIN;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;


UPDATE equipment SET price_per_day = price_per_day + 100 WHERE id = 10;
COMMIT;
-- Если другая транзакция уже изменила эту строку, получим ошибку:
-- ERROR: could not serialize access due to concurrent update
```

---

## Итоговый отчёт

| Тест | Описание | Результат |
|------|----------|-----------|
| Сценарий 1 | Новая аренда (3 таблицы) | ✅ Успех, ошибка, SAVEPOINT |
| Сценарий 2 | Обновление стока | ✅ Успех, ошибка, SAVEPOINT |
| Сценарий 3 | Регистрация + оборудование | ✅ Успех, ошибка, SAVEPOINT |
| Блокировка | Row Level Lock | ✅ Работает |
| READ COMMITTED | Фантомное чтение | ⚠️ Присутствует |
| REPEATABLE READ | Фантомное чтение | ✅ Отсутствует |
| Lost Update | Потерянное обновление | ⚠️ Возможно |
| SERIALIZABLE | Максимальная изоляция | ✅ Гарантирует, но возможны ошибки |
