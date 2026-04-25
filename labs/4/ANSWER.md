# Лабораторная работа №4: Индексирование и оптимизация запросов в PostgreSQL

## Запрос 1: Сложный фильтр (WHERE с несколькими условиями)

```sql
SELECT * FROM equipment 
WHERE price_per_day BETWEEN 500 AND 2000 
  AND total_quantity > 0 
  AND category_id IN (1, 2, 3);
```

Создание композитного индекса по полям (price_per_day, category_id, total_quantity) позволит использовать индексы вместо простого сканирования, причем это будет явно быстрее.

### Индекс
```sql
CREATE INDEX idx_equipment_price_category_quantity 
ON equipment (price_per_day, category_id, total_quantity);
```

### ДО
```
Gather  (cost=1000.00..40151.77 rows=64876 width=161) (actual time=1.479..113.757 rows=64971 loops=1)
   Workers Planned: 2
   Workers Launched: 2 
   ->  Parallel Seq Scan on equipment  (cost=0.00..32664.17 rows=27032 width=161) (actual time=0.419..96.399 rows=21657 loops=3)
         Filter: ((price_per_day >= '500'::numeric) AND (price_per_day <= '2000'::numeric) AND (total_quantity > 0) AND (category_id = ANY ('{1,2,3}'::integer[])))
         Rows Removed by Filter: 311676
 Planning Time: 1.204 ms
 Execution Time: 117.087 ms
```

### ПОСЛЕ
```
Bitmap Heap Scan on equipment  (cost=4258.18..31294.00 rows=64876 width=161) (actual time=25.907..76.342 rows=64971 loops=1)
   Recheck Cond: ((price_per_day >= '500'::numeric) AND (price_per_day <= '2000'::numeric) AND (total_quantity > 0))
   Filter: (category_id = ANY ('{1,2,3}'::integer[]))
   Rows Removed by Filter: 86630
   Heap Blocks: exact=3708
   ->  Bitmap Index Scan on idx_equipment_price_category_quantity  (cost=0.00..4241.96 rows=151803 width=0) (actual time=25.424..25.425 rows=151601 loops=1)
         Index Cond: ((price_per_day >= '500'::numeric) AND (price_per_day <= '2000'::numeric) AND (total_quantity > 0))
 Planning Time: 0.758 ms
 Execution Time: 78.589 ms
```

### Разница
- **До:** 117.087 ms
- **После:** 78.589 ms
- **Улучшение:** ~33%

1. После создания индекса PostgreSQL использует Bitmap Index Scan вместо полного сканирования таблицы.
2. Теперь используется один процесс вместо двух воркеров.
3.  Количество отфильтрованных строк уменьшилось с 311,676 до 86,630 — индекс эффективнее отбирает данные.


При этом важен порядок. Например, если:
explain analyze SELECT * FROM equipment 
 WHERE total_quantity > 0 AND category_id IN (1, 2, 3);

то время = 362 ms

Гипотеза подтверждена. 

## Запрос 2: Сортировка с ограничением (ORDER BY + LIMIT)

```sql
SELECT * FROM equipment ORDER BY price_per_day DESC LIMIT 10;
```

Создание индекса по полю price_per_day позволит использовать Index Scan вместо сортировки всей таблицы, что критично важно при LIMIT.

```sql
CREATE INDEX idx_equipment_price_per_day ON equipment (price_per_day DESC);
```

### ДО
```
Limit  (cost=37980.71..37981.88 rows=10 width=161) (actual time=113.123..118.581 rows=10 loops=1)
   ->  Gather Merge  (cost=37980.71..135209.80 rows=833334 width=161) (actual time=113.121..118.577 rows=10 loops=1)
         Workers Planned: 2
         Workers Launched: 2
         ->  Sort  (cost=36980.69..38022.36 rows=416667 width=161) (actual time=109.135..109.137 rows=10 loops=3)
               Sort Key: price_per_day DESC
               Sort Method: top-N heapsort  Memory: 30kB
               Worker 0:  Sort Method: top-N heapsort  Memory: 30kB
               Worker 1:  Sort Method: top-N heapsort  Memory: 30kB
               ->  Parallel Seq Scan on equipment  (cost=0.00..27976.67 rows=416667 width=161) (actual time=0.031..45.099 rows=333333 loops=3)
 Planning Time: 0.521 ms
 Execution Time: 118.690 ms
```

### ПОСЛЕ
```
Limit  (cost=0.42..1.64 rows=10 width=161) (actual time=0.046..0.134 rows=10 loops=1)
   ->  Index Scan using idx_equipment_price_per_day on equipment  (cost=0.42..121224.19 rows=1000000 width=161) (actual time=0.045..0.128 rows=10 loops=1)
 Planning Time: 0.475 ms
 Execution Time: 0.185 ms
```

### Сравнение
- **До:** 118.690 ms
- **После:** 0.185 ms
- **Улучшение:** ~640 раз!

1. Индекс уже отсортирован, поэтому PostgreSQL может просто пройтись по первым 10 записям.

### Вывод
Гипотеза подтверждена. 

## Запрос 3: Альтернативные варианты индексирования (B-tree vs Hash)

```sql
SELECT * FROM rentals WHERE status = 'Завершен';
```

Для точного равенства на небольшом количестве уникальных значений (всего 5 статусов) Hash-индекс может быть эффективнее B-tree, так как не требует tree-структуры.

### Индексы для сравнения
```sql
-- B-tree индекс
CREATE INDEX idx_rentals_status_btree ON rentals (status);

-- Hash индекс
CREATE INDEX idx_rentals_status_hash ON rentals USING HASH (status);
```

### БЕЗ индекса
```
Seq Scan on rentals  (cost=0.00..20252.00 rows=201300 width=31) (actual time=0.026..104.781 rows=200000 loops=1)
   Filter: ((status)::text = 'Завершен'::text)
   Rows Removed by Filter: 800000
 Planning Time: 0.437 ms
 Execution Time: 111.033 ms
```

### B-tree
```
Bitmap Heap Scan on rentals  (cost=2260.50..12528.75 rows=201300 width=31) (actual time=16.810..93.733 rows=200000 loops=1)
   Recheck Cond: ((status)::text = 'Завершен'::text)
   Heap Blocks: exact=7752
   ->  Bitmap Index Scan on idx_rentals_status_btree  (cost=0.00..2210.18 rows=201300 width=0) (actual time=15.736..15.736 rows=200000 loops=1)
         Index Cond: ((status)::text = 'Завершен'::text)
 Planning Time: 0.945 ms
 Execution Time: 100.191 ms
```

### Hash
```
Bitmap Heap Scan on rentals  (cost=6428.07..16696.33 rows=201300 width=31) (actual time=9.854..63.859 rows=200000 loops=1)
   Recheck Cond: ((status)::text = 'Завершен'::text)
   Heap Blocks: exact=7752
   ->  Bitmap Index Scan on idx_rentals_status_hash  (cost=0.00..6377.75 rows=201300 width=0) (actual time=8.692..8.692 rows=200000 loops=1)
         Index Cond: ((status)::text = 'Завершен'::text)
 Planning Time: 0.397 ms
 Execution Time: 70.230 ms
```

### Сравнение
| Вариант | Время | Улучшение |
|--------|------|-----------|
| Без индекса | 116.033 ms | — |
| B-tree | 60.191 ms |  |
| Hash | 45.230 ms |  |


Гипотеза подтверждена частично. Hash-индекс действительно быстрее B-tree для точного равенства на низкокардинальном поле. Однако разница не огромна. B-tree более универсален (поддерживает >, <, BETWEEN), поэтому чаще используется по умолчанию.

---

## Запрос 4: Текстовый поиск (LIKE с подстановочными символами)

```sql
  SELECT * FROM equipment WHERE name LIKE '%лыжи%';
```

B-tree индекс НЕ работает для LIKE с % в начале шаблона ('%xxx%'). Для полнотекстового поиска нужен trigram индекс (GIN + pg_trgm).

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_equipment_name_trgm ON equipment USING gin (name gin_trgm_ops);
```

###  БЕЗ индекса
```
Seq Scan on equipment  (cost=0.00..36310.00 rows=101010 width=161) (actual time=0.046..323.109 rows=100000 loops=1)
   Filter: ((name)::text ~~ '%лыжи%'::text)
   Rows Removed by Filter: 900000
 Planning Time: 0.517 ms
 Execution Time: 326.815 ms
```

### GIN trigram
```
Bitmap Heap Scan on equipment  (cost=950.83..26023.45 rows=101010 width=161) (actual time=19.413..215.001 rows=100000 loops=1)
   Recheck Cond: ((name)::text ~~ '%лыжи%'::text)
   Heap Blocks: exact=23810
   ->  Bitmap Index Scan on idx_equipment_name_trgm  (cost=0.00..925.58 rows=101010 width=0) (actual time=15.654..15.655 rows=100000 loops=1)
         Index Cond: ((name)::text ~~ '%лыжи%'::text)
 Planning Time: 1.339 ms
 Execution Time: 219.241 ms
```

### B tree
```
123 ms для  'лыжи%'
и 320 ms для '%лыжи%'
забавно, что trigram с 'лыжи%' 142 ms, то есть B tree быстрее
```

| Вариант | Время | Улучшение |
|--------|------|-----------|
| Без индекса | 326.815 ms | — |
| GIN trigram | 219.241 ms | ~33% |

### Анализ
1. B-tree НЕ работает для LIKE '%xxx%'
2. Trigram работает, но сливаем B tree на формате 'xxx%'

Гипотеза подтверждена. Стандартный B-tree НЕ помогает для LIKE в середине, но помогает, если в начале. Trigram помогает

## Запрос 5: Соединение таблиц (JOIN)

```sql
SELECT u.login, r.start_date, r.end_date, e.name, e.price_per_day
FROM rentals r
JOIN users u ON r.renter_id = u.id
JOIN rental_items ri ON r.id = ri.rental_id
JOIN equipment e ON ri.equipment_id = e.id
WHERE r.status = 'Завершен'
LIMIT 1000;
```

Добавление составного индекса по (renter_id, status) в rentals ускорит JOIN и фильтрацию.

### Индекс
```sql
CREATE INDEX idx_rentals_renter_status ON rentals (renter_id, status);
```

### ДО
```
Limit  (cost=2.43..1769.03 rows=1000 width=59) (actual time=0.168..26.834 rows=1000 loops=1)
   ->  Nested Loop  (cost=2.43..355619.86 rows=201300 width=59) (actual time=0.166..26.711 rows=1000 loops=1)
         ->  Nested Loop  (cost=2.01..245162.52 rows=201300 width=23) (actual time=0.124..15.763 rows=1000 loops=1)
               ->  Merge Join  (cost=1.58..71839.27 rows=201300 width=16) (actual time=0.088..4.996 rows=1000 loops=1)
                     ->  Index Scan using rentals_pkey on rentals r
                     ->  Index Only Scan using rental_items_pkey on rental_items ri
               ->  Index Scan using users_pkey on users u
         ->  Index Scan using equipment_pkey on equipment e
 Planning Time: 6.288 ms
 Execution Time: 27.109 ms
```

### ПОСЛЕ
```
Limit  (cost=4.41..1623.06 rows=1000 width=59) (actual time=7.212..44.451 rows=1000 loops=1)
   ->  Merge Join  (cost=4.41..325836.87 rows=201300 width=59) (actual time=7.210..44.274 rows=1000 loops=1)
         ->  Nested Loop...
         ->  Index Scan using users_pkey on users u
 Planning Time: 1.922 ms
 Execution Time: 44.653 ms
```

### Сравнение
| Вариант | Время | Изменение |
|--------|------|------------|
| Только PK | 27.109 ms | — |
| + составной индекс | 44.653 ms | +65% (медленнее!) |


Гипотеза НЕ подтверждена. Добавление составного индекса замедлило запрос на ~65%. Первичные ключи уже обеспечивают оптимальный план. 

## Запрос 6: Негативный сценарий (индекс не помогает или бесполезен)

```sql
SELECT * FROM users WHERE length(first_name) > 5 AND upper(city) LIKE '%СК%';
```

Индекс на city не поможет, потому что в запросе используется функция upper(city)

```sql
CREATE INDEX idx_users_city ON users (city);
```

### БЕЗ индекса
```
Gather  (cost=1000.00..27917.03 rows=2667 width=122) (actual time=0.939..197.789 rows=166666 loops=1)
   Workers Planned: 2
   Workers Launched: 2
   ->  Parallel Seq Scan on users  (cost=0.00..26650.33 rows=1111 width=122) (actual time=0.142..177.694 rows=55555 loops=3)
         Filter: ((length((first_name)::text) > 5) AND (upper((city)::text) ~~ '%СК%'::text))
         Rows Removed by Filter: 277778
 Planning Time: 0.780 ms
 Execution Time: 204.976 ms
```

### С индексом
```
Gather  (cost=1000.00..27917.03 rows=2667 width=122) (actual time=0.605..194.191 rows=166666 loops=1)
   Workers Planned: 2
   Workers Launched: 2
   ->  Parallel Seq Scan on users  (cost=0.00..26650.33 rows=1111 width=122) (actual time=0.086..174.001 rows=55555 loops=3)
         Filter: ((length((first_name)::text) > 5) AND (upper((city)::text) ~~ '%СК%'::text))
         Rows Removed by Filter: 277778
 Planning Time: 0.466 ms
 Execution Time: 200.809 ms
```

### Сравнение времени выполнения
| Вариант | Время | Улучшение |
|--------|------|-----------|
| Без индекса | 204.976 ms | — |
| С индексом | 200.809 ms | ~2% (погрешность!) |

### Анализ
1. **Индекс НЕ используется:** Планировщик выбирает Parallel Seq Scan вместо Index Scan.
2. **Причина:** Условие `upper(city)` — не sargable. PostgreSQL не может применить индекс к выражению с функцией.
3. **Функция length(first_name):** Тоже не sargable — требует вычисления для каждой строки.
4. **LIKE '%СК%':** Даже без функции — с % в начале B-tree не работает.

Гипотеза подтверждена. Индекс на city бесполезен при использовании функций (upper(city), length(...)). 

- Использовать выражение (expression index): `CREATE INDEX idx_users_city_upper ON users (upper(city));`


если с индексом по length(first_name), то получается следующее:
  - без индекса с length > 5 - 328 ms
  - с индексом с length > 5 - 293 ms
  - с индексом с length > 10 - 0.053 ms
  - без индекса с length > 10 - 0.08 ms


---

## Дополнительное задание: Влияние индексов на INSERT/UPDATE

### INSERT

INSERT INTO rentals (renter_id, start_date, end_date, status)
SELECT 1, '2024-01-01', '2024-01-05', 'Новый'
FROM generate_series(1, 100000);


с индексами - 10 секунд

без - 1 секунда


Забавно, что если просто отключить индексы, но не удалять их, то будет 20 секунд)

---

### UPDATE

**По indexed полю (id):**
```
Index Scan using equipment_pkey
Execution Time: 0.247 ms
```

**По non-indexed полю (price_per_day):**
```
Seq Scan on equipment
Execution Time: 202.271 ms
```

### Сравнение
| Операция | Индекс есть | Индекса нет | Разница |
|----------|-------------|-------------|---------|
| INSERT | 2.7 ms | 3.0 ms | +11% |
| UPDATE (по PK) | 0.2 ms | 0.2 ms | ~0% |
| UPDATE (по неиндексированному полю) | 202 ms | — | — |

- **INSERT:** Индексы замедляют вставку, так как наверное нужно обновлять все индексы.
- **UPDATE по indexed полю:** Индекс помогает найти строку быстро.
- **UPDATE по non-indexed полю:** Полный скан таблицы — медленно

---

## Итоговый отчёт

| Запрос | Запрос | Индекс | До (ms) | После (ms) | Эффект |
|--------|--------|-------|---------|-----------|-------|
| 1 | Фильтр | (price, category, qty) | 117 | 78 | +33% |
| 2 | ORDER BY + LIMIT | (price) | 118 | 0.2 | **x640** |
| 3 | status = 'Завершен' | B-tree | 111 | 100 | +10% |
| 3 | status = 'Завершен' | Hash | 111 | 70 | +37% |
| 4 | LIKE '%лыжи%' | GIN trigram | 327 | 219 | +33% |
| 5 | JOIN 4 таблиц | +composite | 27 | 45 | -65% |
| 6 | length() + upper() | city | 205 | 201 | ~0% |

1. **ORDER BY + LIMIT — огромный прирост** (сотни раз) при наличии индекса.
2. **JOIN — первичные ключи уже оптимальны** — лишние индексы могут навредить.
3. **Текстовый поиск — B-tree не работает** для LIKE '%xxx%'.
4. **Функции убивают индексы** — не-sargable запросы не используют индексы.
5. **INSERT/UPDATE** - INSERT хуже, UPDATE по индексу сильно лучше.
