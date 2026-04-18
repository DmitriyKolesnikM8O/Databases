## 2

- Функция, которая возвращает полную стоимость аренды. 
```sql
CREATE OR REPLACE FUNCTION get_rental_total_price(p_rental_id INTEGER)
RETURNS NUMERIC AS $$
DECLARE
    v_total NUMERIC := 0;
    v_days INTEGER;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM rentals WHERE id = p_rental_id) THEN
        RAISE EXCEPTION 'Аренда с ID % не найдена', p_rental_id;
    END IF;

    SELECT (end_date - start_date) + 1 INTO v_days 
    FROM rentals 
    WHERE id = p_rental_id;

    SELECT SUM(price_at_booking * quantity) INTO v_total
    FROM rental_items
    WHERE rental_id = p_rental_id;

    RETURN COALESCE(v_total, 0) * v_days;

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Ошибка в функции get_rental_total_price: %', SQLERRM;
        RETURN 0;
END;
$$ LANGUAGE plpgsql;
```



- процедура для добавления товара в существующую аренду.
```sql
CREATE OR REPLACE PROCEDURE add_item_to_rental(
    p_rental_id INTEGER,
    p_equipment_id INTEGER,
    p_quantity INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_current_price NUMERIC;
    v_stock INTEGER;
    v_rental_status VARCHAR;
BEGIN

    SELECT status INTO v_rental_status
    FROM rentals
    WHERE id = p_rental_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Аренды с ID % не существует', p_rental_id;
    END IF;

    IF v_rental_status != 'Новый' THEN
        RAISE EXCEPTION 'Бизнес-ошибка: добавление в НЕ новую аренду';
    END IF;



    IF p_quantity <= 0 THEN
        RAISE EXCEPTION 'Количество должно быть положительным';
    END IF;

    
    SELECT price_per_day, total_quantity INTO v_current_price, v_stock 
    FROM equipment 
    WHERE id = p_equipment_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Товар с ID % не существует', p_equipment_id;
    END IF;

    IF p_quantity > v_stock THEN
        RAISE EXCEPTION 'Недостаточно товара (ID %). Запрошено: %, В наличии: %', 
                        p_equipment_id, p_quantity, v_stock;
    END IF;

    INSERT INTO rental_items (rental_id, equipment_id, quantity, price_at_booking)
    VALUES (p_rental_id, p_equipment_id, p_quantity, v_current_price);

    RAISE NOTICE 'Товар успешно добавлен в аренду №%', p_rental_id;

EXCEPTION
    WHEN foreign_key_violation THEN
        RAISE EXCEPTION 'Бизнес-ошибка: Аренды с ID % не существует в системе.', p_rental_id;
    
    WHEN unique_violation THEN
        RAISE EXCEPTION 'Бизнес-ошибка: Товар % уже добавлен в аренду %. Используйте UPDATE для изменения количества.', 
                        p_equipment_id, p_rental_id;

    WHEN OTHERS THEN
        RAISE EXCEPTION 'Непредвиденная ошибка системы: %', SQLERRM;
END;
$$;
```

// CALL add_item_to_rental(1, 4, 1);
// CALL add_item_to_rental(1, 1, 100); - ошибка, так как столько лыж нет
// CALL add_item_to_rental(999, 1, 1); - ошибка, так как такой аренды не существует

- функция: общее количество аренд, который этот пользователь когда-либо оформлял
```sql
CREATE OR REPLACE FUNCTION get_total_rentals_by_userId(user_id INTEGER)
RETURNS INT AS $$
DECLARE
    total_rentals INT := 0;
BEGIN

    IF NOT EXISTS (SELECT 1 FROM users WHERE id=user_id) THEN
        RAISE EXCEPTION 'Пользователя с ID % не существует', user_id;
    END IF;

    SELECT COUNT(*) INTO total_rentals
    FROM rentals
    WHERE renter_id=user_id;

    RETURN total_rentals;
    

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Ошибка в функции get_total_rentals_by_userId: %', SQLERRM;
        RETURN 0;
END;
$$ LANGUAGE plpgsql;
```

## 3

- Проверять наличие инвентаря перед добавлением в аренду.

```sql
CREATE OR REPLACE FUNCTION fn_check_stock_availability()
RETURNS TRIGGER AS $$
DECLARE
    v_available INTEGER;
BEGIN
    SELECT total_quantity INTO v_available 
    FROM equipment 
    WHERE id = NEW.equipment_id;

    IF NEW.quantity > v_available THEN
        RAISE EXCEPTION 'Бизнес-правило нарушено: Недостаточно товара (ID %). В наличии: %, Запрошено: %', 
                        NEW.equipment_id, v_available, NEW.quantity;
    END IF;

    RETURN NEW;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Ошибка в триггере fn_check_stock_availability: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_stock_before_rental
BEFORE INSERT OR UPDATE ON rental_items
FOR EACH ROW
EXECUTE FUNCTION fn_check_stock_availability();
```

- улучшенный предыдущий триггер: проверяет реальное остаточное количество товара
```sql
CREATE OR REPLACE FUNCTION fn_check_stock_availability()
RETURNS TRIGGER AS $$
DECLARE
    v_available INTEGER;
    v_in_rental INTEGER;
BEGIN
    SELECT total_quantity INTO v_available 
    FROM equipment 
    WHERE id = NEW.equipment_id;

    SELECT COALESCE(SUM(ri.quantity), 0) INTO v_in_rental
    FROM rental_items ri
    JOIN rentals r ON ri.rental_id=r.id
    WHERE ri.equipment_id=NEW.equipment_id AND r.status IN ('Новый', 'В процессе', 'Оплачен') AND ri.id != NEW.id;

    IF NEW.quantity > (v_available - v_in_rental) THEN
        RAISE EXCEPTION 'Бизнес-правило нарушено: Недостаточно товара (ID %). В наличии: %, Запрошено: %', 
                        NEW.equipment_id, v_available, NEW.quantity;
    END IF;

    RETURN NEW;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Ошибка в триггере fn_check_stock_availability: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_stock_before_rental
BEFORE  UPDATE ON rental_items
FOR EACH ROW
EXECUTE FUNCTION fn_check_stock_availability();
```

- защита уже завершенного заказа
```sql
CREATE OR REPLACE FUNCTION fn_protect_finished_rental()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' AND OLD.status = 'Завершен' THEN
        RAISE EXCEPTION 'Бизнес-ошибка: Заказ №% уже завершен. Изменение данных запрещено!', OLD.id;
    END IF;

    IF NEW.status NOT IN ('Новый', 'В процессе', 'Оплачен', 'Завершен', 'Отменен') THEN
        RAISE EXCEPTION 'Ошибка: Недопустимый статус заказа: %', NEW.status;
    END IF;

    RETURN NEW;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Ошибка при обновлении статуса: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_lock_finished_rental
BEFORE INSERT OR UPDATE ON rentals
FOR EACH ROW
EXECUTE FUNCTION fn_protect_finished_rental();
```

- триггер, который будет автоматически обновлять поле "Дата последнего изменения" в users
```sql
CREATE OR REPLACE FUNCTION fn_update_user_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_user_update_audit
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION fn_update_user_timestamp();
```


## 5

- Попробуем продлить срок аренды для уже закрытого заказа.
```sql
UPDATE rentals 
SET end_date = '2025-12-31' 
WHERE id = 1;
```

Бизнес-ошибка: Заказ №1 уже завершен. Изменение данных запрещено!

- больше товара, чем есть
```sql
CALL add_item_to_rental(12, 14, 100);
```

Недостаточно товара (ID 14). Запрошено: 100, В наличии: 2

- добавляем товар в аренду, а его нет
```sql
CALL add_item_to_rental(999, 1, 1);
```

Аренды с ID 999 не существует в системе.

- добавляем в аренду то, что уже там есть
```sql
CALL add_item_to_rental(12, 15, 1);
```

Бизнес-ошибка: Товар 15 уже добавлен в аренду 12. Используйте UPDATE для изменения количества.

- берем уже завершенный заказ и пытаемся изменить его статус
```sql
UPDATE rentals SET status = 'Сломано' WHERE id = 12;
```

Бизнес-ошибка: Заказ №12 уже завершен. Изменение данных запрещено!

- пытаемся изменить дату начала у уже завершенного заказа
```sql
UPDATE rentals SET start_date = '2020-01-01' WHERE id = 1;
```

Ошибка при обновлении статуса: Бизнес-ошибка: Заказ №12 уже завершен. Изменение данных запрещено!

- перевод заказа, который "В процессе" в статус "Оплачен"
```sql
UPDATE rentals SET status = 'Оплачен' WHERE id = 7;
```

Your call!
UPDATE 1

- проверка, что триггер на автообновление времени последнего изменения работает
```sql
SELECT id, login, updated_at FROM users WHERE id = 1;

UPDATE users SET first_name = 'Чебурашка Гондурасский' WHERE id = 1;

SELECT id, login, updated_at FROM users WHERE id = 1; //время обновится
```

