ALTER TABLE rental_items DISABLE TRIGGER trg_check_stock_before_rental;

TRUNCATE TABLE reviews, payments, rental_items, rentals, equipment, users, categories RESTART IDENTITY CASCADE;

INSERT INTO categories (name, description) VALUES 
('Зимний спорт', 'Лыжи, сноуборды и аксессуары для зимы'),
('Велоспорт', 'Горные, городские и шоссейные велосипеды'),
('Кемпинг', 'Палатки, спальники и походное снаряжение'),
('Водный спорт', 'Сап-борды, байдарки и спасательные жилеты'),
('Активные игры', 'Мячи, ракетки для тенниса и бадминтона'),
('Альпинизм', 'Страховочные тросы, каски, кошки'),
('Теннис', 'Ракетки, мячи, сетки');

INSERT INTO users (first_name, last_name, patronymic, login, password_hash, phone, city)
SELECT 
    CASE (i % 20) 
        WHEN 0 THEN 'Александр' WHEN 1 THEN 'Андрей' WHEN 2 THEN 'Антон' WHEN 3 THEN 'Борис'
        WHEN 4 THEN 'Василий' WHEN 5 THEN 'Владимир' WHEN 6 THEN 'Дмитрий' WHEN 7 THEN 'Евгений'
        WHEN 8 THEN 'Иван' WHEN 9 THEN 'Игорь' WHEN 10 THEN 'Константин' WHEN 11 THEN 'Максим'
        WHEN 12 THEN 'Михаил' WHEN 13 THEN 'Никита' WHEN 14 THEN 'Олег' WHEN 15 THEN 'Павел'
        WHEN 16 THEN 'Петр' WHEN 17 THEN 'Сергей' WHEN 18 THEN 'Федор' WHEN 19 THEN 'Юрий'
    END,
    CASE (i % 30)
        WHEN 0 THEN 'Иванов' WHEN 1 THEN 'Петров' WHEN 2 THEN 'Сидоров' WHEN 3 THEN 'Кузнецов'
        WHEN 4 THEN 'Смирнов' WHEN 5 THEN 'Васильев' WHEN 6 THEN 'Федоров' WHEN 7 THEN 'Алексеев'
        WHEN 8 THEN 'Соколов' WHEN 9 THEN 'Яковлев' WHEN 10 THEN 'Попов' WHEN 11 THEN 'Лебедев'
        WHEN 12 THEN 'Волков' WHEN 13 THEN 'Зайцев' WHEN 14 THEN 'Павлов' WHEN 15 THEN 'Козлов'
        WHEN 16 THEN 'Макаров' WHEN 17 THEN 'Николаев' WHEN 18 THEN 'Морозов' WHEN 19 THEN 'Тихонов'
        WHEN 20 THEN 'Орлов' WHEN 21 THEN 'Киселев' WHEN 22 THEN 'Григорьев' WHEN 23 THEN 'Богданов'
        WHEN 24 THEN 'Осипов' WHEN 25 THEN 'Савельев' WHEN 26 THEN 'Калинин' WHEN 27 THEN 'Антонов'
        WHEN 28 THEN 'Якубов' WHEN 29 THEN 'Миронов'
    END,
    CASE WHEN i % 3 = 0 THEN 
        CASE (i % 10) WHEN 0 THEN 'Александрович' WHEN 1 THEN 'Андреевич' WHEN 2 THEN 'Иванович'
            WHEN 3 THEN 'Петрович' WHEN 4 THEN 'Сергеевич' WHEN 5 THEN 'Дмитриевич' WHEN 6 THEN 'Владмимирович'
            WHEN 7 THEN 'Николаевич' WHEN 8 THEN 'Константинович' WHEN 9 THEN 'Михайлович' END
    END,
    'user_' || i,
    'hash_' || substring(md5(i::text) from 1 for 16),
    '+79' || LPAD(((100000000 + (i * 7 + 13) % 900000000))::text, 9, '0'),
    (ARRAY['Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Казань', 
          'Нижний Новгород', 'Самара', 'Омск', 'Уфа', 'Красноярск',
          'Воронеж', 'Пермь', 'Волгоград', 'Краснодар', 'Саратов'])[1 + (i % 15)]
FROM generate_series(1, 1000000) AS i;

INSERT INTO equipment (owner_id, category_id, name, description, price_per_day, total_quantity)
SELECT 
    1 + ((i * 17 + 3) % 1000000),                                          
    1 + (i % 7),                                                       
    CASE (i % 10)
        WHEN 0 THEN 'Горные лыжи' WHEN 1 THEN 'Сноуборд' WHEN 2 THEN 'Велосипед горный'
        WHEN 3 THEN 'Велосипед шоссейный' WHEN 4 THEN 'Палатка 2-местная'
        WHEN 5 THEN 'Палатка 4-местная' WHEN 6 THEN 'Сап-борд' WHEN 7 THEN 'Спальный мешок'
        WHEN 8 THEN 'Ракетки теннисные' WHEN 9 THEN 'Мяч футбольный'
    END || ' #' || i,
    'Качественное снаряжение для активного отдыха. Модель: ' || (2020 + (i % 10)),
    100 + (i % 9900),                                                    
    1 + (i % 100)                                                       
FROM generate_series(1, 1000000) AS i;

INSERT INTO rentals (renter_id, start_date, end_date, status)
SELECT 
    1 + ((i * 23 + 5) % 1000000),                                        
    DATE '2023-01-01' + ((i * 11) % 730),                                 
    DATE '2023-01-01' + ((i * 11) % 730) + 1 + (i % 14),              
    (ARRAY['Новый', 'В процессе', 'Оплачен', 'Завершен', 'Отменен'])[1 + (i % 5)]
FROM generate_series(1, 1000000) AS i;

INSERT INTO rental_items (rental_id, equipment_id, quantity, price_at_booking)
SELECT 
    1 + ((i * 19 + 7) % 1000000),                                        
    1 + ((i * 31 + 11) % 1000000),                                       
    1 + (i % 10),                                                       
    100 + (i % 9900)                                                    
FROM generate_series(1, 1000000) AS i;

INSERT INTO payments (rental_id, payment_amount, payment_date, status)
SELECT 
    1 + ((i * 13 + 2) % 1000000),                                        
    100 + (i % 99900),                                                    
    DATE '2023-01-01' + ((i * 17) % 730),                                 
    CASE WHEN (i % 10) < 9 THEN 'Успешно' ELSE 'Отклонен' END             
FROM generate_series(1, 1000000) AS i;

INSERT INTO reviews (renter_id, equipment_id, rating, review_text, created_at)
SELECT 
    1 + ((i * 29 + 3) % 1000000),                                        
    1 + ((i * 37 + 5) % 1000000),                                        
    1 + (i % 5),                                                       
    CASE (i % 5)
        WHEN 0 THEN 'Отличное качество, рекомендую!'
        WHEN 1 THEN 'Хороший товар, нормальное соотношение цена/качество'
        WHEN 2 THEN 'Среднее качество, есть недостатки'
        WHEN 3 THEN 'Не очень, но за такую цену пойдет'
        WHEN 4 THEN 'Ужасное качество, жалею о покупке'
    END || ' #' || i,
    DATE '2023-01-01' + ((i * 23) % 730)                                   
FROM generate_series(1, 1000000) AS i;

SELECT 'categories' AS table_name, COUNT(*) AS row_count FROM categories
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'equipment', COUNT(*) FROM equipment
UNION ALL
SELECT 'rentals', COUNT(*) FROM rentals
UNION ALL
SELECT 'rental_items', COUNT(*) FROM rental_items
UNION ALL
SELECT 'payments', COUNT(*) FROM payments
UNION ALL
SELECT 'reviews', COUNT(*) FROM reviews
ORDER BY 1;

ALTER TABLE rental_items ENABLE TRIGGER trg_check_stock_before_rental;
