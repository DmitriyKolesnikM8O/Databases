# Лабораторная работа №6: Разработка RESTful API

## Структура проекта

```
labs/6/
├── main.py          # FastAPI приложение
├── models.py       # SQLAlchemy модели
├── schemas.py     # Pydantic схемы
├── requirements.txt
└── venv/          # Виртуальное окружение
```

## Запуск

```bash
cd /home/ares/Databases/labs/6
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

API будет доступно на:
- **http://localhost:8000** — основной endpoint
- **http://localhost:8000/docs** — Swagger UI
- **http://localhost:8000/redoc** — ReDoc

---

## Полный список endpoints

### Categories (CRUD)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/categories` | Список категорий (пагинация) |
| GET | `/categories/{id}` | Категория по ID |
| POST | `/categories` | Создание категории |
| PUT | `/categories/{id}` | Полное обновление |
| DELETE | `/categories/{id}` | Удаление |

### Users (CRUD + фильтрация + сортировка)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/users` | Список (пагинация, фильтр city, сортировка sort/order) |
| GET | `/users/{id}` | Пользователь по ID |
| POST | `/users` | Создание пользователя |
| PATCH | `/users/{id}` | Частичное обновление |
| DELETE | `/users/{id}` | Удаление |

### Equipment (CRUD + фильтрация + сортировка)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/equipment` | Список (пагинация, фильтры category_id/owner_id/min_price/max_price, сортировка) |
| GET | `/equipment/{id}` | Оборудование по ID |
| POST | `/equipment` | Создание |
| PATCH | `/equipment/{id}` | Частичное обновление |
| DELETE | `/equipment/{id}` | Удаление |

### Rentals (CRUD)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/rentals` | Список (пагинация, фильтр renter_id/status) |
| GET | `/rentals/{id}` | Аренда по ID |
| POST | `/rentals` | Создание |
| PATCH | `/rentals/{id}` | Частичное обновление |
| DELETE | `/rentals/{id}` | Удаление |

### Rental Items

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/rentals/{id}/items` | Товары в аренде |
| POST | `/rentals/{id}/items` | Добавить товар |

### Payments

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/payments` | Список |
| POST | `/payments` | Создание |

### Reviews

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/reviews` | Список (фильтр equipment_id) |
| POST | `/reviews` | Создание |

### Views

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/views/equipment-catalog` | Каталог оборудования |
| GET | `/views/rental-details` | Детализация аренд |
| GET | `/views/client-activity` | Активность клиентов |

### Reports

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/reports/sales-by-category` | Продажи по категориям |
| GET | `/reports/top-customers` | Топ клиентов |
| GET | `/reports/top-equipment` | Топ оборудования |

### Functions (из лабы 3)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/users/{id}/rentals-count` | Количество аренд |
| GET | `/rentals/{id}/total-price` | Общая стоимость |

### Health

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/` | Корневой |
| GET | `/health` | Проверка |

---

## Коды ответа HTTP

| Код | Описание |
|-----|---------|
| 200 | Успех |
| 201 | Создано |
| 204 | Нет содержимого |
| 400 | Ошибка валидации (некорректные данные) |
| 404 | Не найдено |
| 422 | Ошибка обработки (недопустимые параметры) |
| 500 | Внутренняя ошибка сервера |

---

## Обработка ошибок (все сценарии)

### 1. Category не найдена (404)

```bash
curl http://localhost:8000/categories/999999
# Ответ: {"detail":"Category not found"}

curl http://localhost:8000/categories/2000000
# Ответ: {"detail":"Category not found"}
```

### 2. User не найден (404)

```bash
curl http://localhost:8000/users/999999
# Для существующего ID=999999 - вернёт данные

curl http://localhost:8000/users/2000000
# Ответ: {"detail":"User not found"}
```

### 3. Equipment не найден (404)

```bash
curl http://localhost:8000/equipment/999999
# Для существующего ID - вернёт данные

curl http://localhost:8000/equipment/2000000
# Ответ: {"detail":"Equipment not found"}
```

### 4. Rental не найден (404)

```bash
curl http://localhost:8000/rentals/2000000
# Ответ: {"detail":"Rental not found"}
```

### 5. Отрицательный ID (422 через Pydantic валидацию)

```bash
curl "http://localhost:8000/equipment?page=0"
# HTTP: 422
# Ответ: {"detail":[{"type":"greater_than_equal","loc":["query","page"]...}]}

curl "http://localhost:8000/equipment?limit=0"
# HTTP: 422
# Ответ: {"detail":[{"type":"greater_than_equal","loc":["query","limit"]...}]}
```

### 6. Отрицательный ID в хранимых функциях (400)

```bash
curl http://localhost:8000/users/-1/rentals-count
# Ответ: {"detail":"ID пользователя должен быть положительным числом"}

curl http://localhost:8000/rentals/-1/total-price
# Ответ: {"detail":"ID аренды должен быть положительным числом"}
```

### 7. Большой несуществующий ID в функциях (404)

```bash
curl http://localhost:8000/users/100000000/rentals-count
# Ответ: {"detail":"Пользователь с ID=100000000 не найден"}

curl http://localhost:8000/rentals/100000000/total-price
# Ответ: {"detail":"Аренда с ID=100000000 не найдена"}
```

### 8. Ошибка валидации при создании (422)

```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"first_name": "", "login": "", "password_hash": "x"}'
# HTTP: 422
# Ответ: validation error для пустых полей
```

### 9. Дублирование уникального поля (400)

```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"login":"user_1","password_hash":"x","phone":"+79100000020","city":"Москва"}'
# HTTP: 400 (PostgreSQL error from SQLAlchemy)
```

### Успешные примеры

```bash
# GET с пагинацией
curl "http://localhost:8000/users?page=1&limit=10"

# GET с фильтрацией
curl "http://localhost:8000/equipment?category_id=1&min_price=100&max_price=500"

# GET с сортировкой
curl "http://localhost:8000/equipment?sort=price_per_day&order=desc"

# POST создание
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Иван","last_name":"Иванов","login":"ivan_test","password_hash":"hash","phone":"+79990000001","city":"Москва"}'

# PATCH обновление
curl -X PATCH http://localhost:8000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Новое имя"}'

# DELETE
curl -X DELETE http://localhost:8000/categories/8
```

---

## Технологии

- **FastAPI** — веб-фреймворк
- **SQLAlchemy** — ORM
- **Pydantic** — валидация
- **uvicorn** — ASGI сервер
- **PostgreSQL** — база данных
