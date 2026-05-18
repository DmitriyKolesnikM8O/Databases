# Лабораторная работа №6: Разработка RESTful API для системы аренды оборудования

## Содержание

1. [Общее описание проекта](#1-общее-описание-проекта)
2. [Технологический стек](#2-технологический-стек)
3. [Структура базы данных](#3-структура-базы-данных)
4. [Установка и запуск](#4-установка-запуск)
5. [Полный список всех endpoints](#5-полный-список-всех-endpoints)
6. [Детальное описание каждого endpoint](#6-детальное-описание-каждого-endpoint)
7. [Параметры запросов и фильтрации](#7-параметры-запросов-и-фильтрации)
8. [Коды ответа HTTP](#8-коды-ответа-http)
9. [Обработка ошибок](#9-обработка-ошибок)
10. [Валидация данных](#10-валидация-данных)
11. [Примеры запросов](#11-примеры-запросов)
12. [Пагинация](#12-пагинация)
13. [Сортировка](#13-сортировка)
14. [Views (представления БД)](#14-views-представления-бд)
15. [Агрегационные отчеты](#15-агрегационные-отчеты)
16. [Хранимые функции](#16-хранимые-функции)
17. [Вопросы для защиты](#17-вопросы-для-защиты)

---

## 1. Общее описание проекта

**Название проекта:** Rental Equipment API (RESTful API для системы аренды оборудования)

**Версия:** 1.0.0

**Назначение:** RESTful API для базы данных системы аренды оборудования, позволяющий выполнять полный CRUD (Create, Read, Update, Delete) операции над всеми сущностями базы данных, а также получать агрегационные отчеты и данные из представлений.

**Основные возможности:**
- Управление категориями оборудования
- Управление пользователями системы
- Управление оборудованием для аренды
- Управление арендами и арендуемыми товарами
- Управление платежами
- Управление отзывами
- Получение данных из представлений (views)
- Генерация агрегационных отчетов
- Вызов хранимых функций базы данных

---

## 2. Технологический стек

| Технология | Версия | Назначение |
|------------|--------|-----------|
| **FastAPI** | 0.136.1 | Веб-фреймворк для создания REST API |
| **SQLAlchemy** | 2.0.49 | ORM для работы с базой данных |
| **Pydantic** | 2.13.3 | Валидация данных и сериализация |
| **psycopg2-binary** | 2.9.12 | Драйвер PostgreSQL для Python |
| **uvicorn** | 0.46.0 | ASGI-сервер для запуска приложения |
| **PostgreSQL** | - | СУБД (предполагается в задании) |

**Архитектура паттерна:**
- **MVC-подобная структура:**
  - `models.py` - Model (модели SQLAlchemy)
  - `schemas.py` - View/Schema (схемы Pydantic для валидации и сериализации)
  - `main.py` - Controller (бизнес-логика и endpoints)

---

## 3. Структура базы данных

### 3.1 Таблицы

#### Таблица `categories` (Категории)
| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| id | INTEGER | PRIMARY KEY | Уникальный идентификатор |
| name | VARCHAR(256) | UNIQUE, NOT NULL | Название категории |
| description | TEXT | NULL | Описание категории |

**Связи:** one-to-many с `equipment` (категория может содержать много единиц оборудования)

---

#### Таблица `users` (Пользователи)
| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| id | INTEGER | PRIMARY KEY | Уникальный идентификатор |
| first_name | VARCHAR(256) | NOT NULL | Имя |
| last_name | VARCHAR(256) | NULL | Фамилия |
| patronymic | VARCHAR(256) | NULL | Отчество |
| login | VARCHAR(256) | UNIQUE, NOT NULL | Логин |
| password_hash | VARCHAR(256) | NOT NULL | Хэш пароля |
| phone | VARCHAR(20) | UNIQUE, NOT NULL | Телефон |
| city | VARCHAR(100) | NOT NULL | Город |

**Связи:**
- one-to-many с `equipment` (пользователь может владеть многим оборудованием)
- one-to-many с `rentals` (пользователь может быть арендатором многих аренд)
- one-to-many с `reviews` (пользователь может оставлять много отзывов)

---

#### Таблица `equipment` (Оборудование)
| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| id | INTEGER | PRIMARY KEY | Уникальный идентификатор |
| owner_id | INTEGER | FOREIGN KEY, NOT NULL | ID владельца (ссылка на users) |
| category_id | INTEGER | FOREIGN KEY, NOT NULL | ID категории (ссылка на categories) |
| name | VARCHAR(256) | NOT NULL | Название оборудования |
| description | TEXT | NULL | Описание |
| price_per_day | NUMERIC(10,2) | NOT NULL | Цена за день аренды |
| total_quantity | INTEGER | NOT NULL, DEFAULT 0 | Общее количество |

**Связи:**
- many-to-one с `users` (владелец)
- many-to-one с `categories` (категория)
- one-to-many с `rental_items` (оборудование может быть во многих арендах)
- one-to-many с `reviews` (оборудование может иметь много отзывов)

**Внешние ключи:**
- `owner_id` -> `users(id)` с ON DELETE CASCADE
- `category_id` -> `categories(id)` с ON DELETE RESTRICT

---

#### Таблица `rentals` (Аренды)
| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| id | INTEGER | PRIMARY KEY | Уникальный идентификатор |
| renter_id | INTEGER | FOREIGN KEY, NOT NULL | ID арендатора (ссылка на users) |
| start_date | DATE | NOT NULL | Дата начала аренды |
| end_date | DATE | NOT NULL | Дата окончания аренды |
| status | VARCHAR(50) | NOT NULL, DEFAULT 'Новый' | Статус аренды |

**Связи:**
- many-to-one с `users` (арендатор)
- one-to-many с `rental_items` (аренда может содержать много позиций)
- one-to-many с `payments` (аренда может иметь много платежей)

**Внешние ключи:**
- `renter_id` -> `users(id)` с ON DELETE CASCADE

---

#### Таблица `rental_items` (Позиции аренды)
| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| rental_id | INTEGER | PRIMARY KEY, FOREIGN KEY | ID аренды |
| equipment_id | INTEGER | PRIMARY KEY, FOREIGN KEY | ID оборудования |
| quantity | INTEGER | NOT NULL | Количество единиц |
| price_at_booking | NUMERIC(10,2) | NOT NULL | Цена на момент бронирования |

**Связи:**
- many-to-one с `rentals` (позиция принадлежит аренде)
- many-to-one с `equipment` (позиция ссылается на оборудование)

**Внешние ключи:**
- `rental_id` -> `rentals(id)` с ON DELETE CASCADE
- `equipment_id` -> `equipment(id)` с ON DELETE CASCADE

**Примечание:** Составной первичный ключ (rental_id, equipment_id)

---

#### Таблица `payments` (Платежи)
| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| id | INTEGER | PRIMARY KEY | Уникальный идентификатор |
| rental_id | INTEGER | FOREIGN KEY, NOT NULL | ID аренды |
| payment_amount | NUMERIC(10,2) | NOT NULL | Сумма платежа |
| payment_date | DATE | NOT NULL | Дата платежа |
| status | VARCHAR(50) | NOT NULL | Статус платежа |

**Связи:**
- many-to-one с `rentals` (платеж принадлежит аренде)

**Внешние ключи:**
- `rental_id` -> `rentals(id)` с ON DELETE CASCADE

---

#### Таблица `reviews` (Отзывы)
| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| id | INTEGER | PRIMARY KEY | Уникальный идентификатор |
| renter_id | INTEGER | FOREIGN KEY, NOT NULL | ID автора отзыва |
| equipment_id | INTEGER | FOREIGN KEY, NOT NULL | ID оборудования |
| rating | INTEGER | NOT NULL | Рейтинг (1-5) |
| review_text | TEXT | NULL | Текст отзыва |
| created_at | DATE | NOT NULL | Дата создания отзыва |

**Связи:**
- many-to-one с `users` (автор отзыва)
- many-to-one с `equipment` (оборудование)

**Внешние ключи:**
- `renter_id` -> `users(id)` с ON DELETE CASCADE
- `equipment_id` -> `equipment(id)` с ON DELETE CASCADE

---

### 3.2 Представления (Views)

#### Представление `v_equipment_catalog` (Каталог оборудования)
Представляет объединенную информацию об оборудовании с именем категории, владельца и средним рейтингом.

| Поле | Тип | Описание |
|------|-----|----------|
| equipment_id | INTEGER | ID оборудования |
| equipment_name | VARCHAR(256) | Название оборудования |
| category_name | VARCHAR(256) | Название категории |
| price_per_day | NUMERIC(10,2) | Цена за день |
| owner_name | VARCHAR(512) | Имя владельца (ФИО) |
| avg_rating | NUMERIC(10,2) | Средний рейтинг |

---

#### Представление `v_rental_details` (Детализация аренд)
Представляет детальную информацию об арендах с указанием товаров и статусов.

| Поле | Тип | Описание |
|------|-----|----------|
| rental_id | INTEGER | ID аренды |
| customer_name | VARCHAR(512) | Имя клиента (ФИО) |
| item_name | VARCHAR(256) | Название товара |
| start_date | DATE | Дата начала |
| end_date | DATE | Дата окончания |
| price_at_booking | NUMERIC(10,2) | Цена на момент бронирования |
| status | VARCHAR(50) | Статус аренды |

---

#### Представление `v_client_activity` (Активность клиентов)
Представляет статистику активности клиентов.

| Поле | Тип | Описание |
|------|-----|----------|
| user_id | INTEGER | ID пользователя |
| full_name | VARCHAR(512) | Полное имя |
| city | VARCHAR(100) | Город |
| total_rentals | INTEGER | Всего аренд |
| total_spent | NUMERIC(10,2) | Общая сумма потраченных средств |
| last_rental_date | DATE | Дата последней аренды |

---

### 3.3 Хранимые функции (из лабораторной работы №3)

#### Функция `get_total_rentals_by_userId(user_id INTEGER)`
Возвращает общее количество аренд для указанного пользователя.

**Параметры:**
- `user_id` - INTEGER - ID пользователя

**Возвращает:**
- INTEGER - количество аренд

---

#### Функция `get_rental_total_price(rental_id INTEGER)`
Возвращает общую стоимость аренды.

**Параметры:**
- `rental_id` - INTEGER - ID аренды

**Возвращает:**
- NUMERIC(10,2) - общая стоимость аренды

---

## 4. Установка и запуск

### 4.1 Требования

- Python 3.10+
- PostgreSQL
- pip (менеджер пакетов Python)

### 4.2 Установка зависимостей

```bash
cd /home/ares/Databases/labs/6
source venv/bin/activate
pip install -r requirements.txt
```

### 4.3 Запуск сервера

```bash
cd /home/ares/Databases/labs/6
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 4.4 Доступ к API

После запуска приложение доступно по следующим адресам:

| Адрес | Описание |
|-------|----------|
| http://localhost:8000 | Корневой endpoint (health check) |
| http://localhost:8000/health | Проверка состояния API |
| http://localhost:8000/docs | Swagger UI (интерактивная документация) |
| http://localhost:8000/redoc | ReDoc (альтернативная документация) |

### 4.5 Конфигурация базы данных

Строка подключения к базе данных находится в файле `models.py`:

```python
DATABASE_URL = "postgresql://user:password@localhost:5432/bigdata_db"
```

**Структура подключения:**
- Протокол: `postgresql`
- Пользователь: `user`
- Пароль: `password`
- Хост: `localhost`
- Порт: `5432`
- Имя БД: `bigdata_db`

---

## 5. Полный список всех endpoints

### 5.1 Categories (Категории) - CRUD

| № | Метод | Endpoint | Описание | Статус |
|---|-------|----------|----------|--------|
| 1 | GET | `/categories` | Получить список категорий с пагинацией | ✅ |
| 2 | GET | `/categories/{category_id}` | Получить категорию по ID | ✅ |
| 3 | POST | `/categories` | Создать новую категорию | ✅ |
| 4 | PUT | `/categories/{category_id}` | Полностью обновить категорию | ✅ |
| 5 | DELETE | `/categories/{category_id}` | Удалить категорию | ✅ |

### 5.2 Users (Пользователи) - CRUD + фильтрация + сортировка

| № | Метод | Endpoint | Описание | Статус |
|---|-------|----------|----------|--------|
| 6 | GET | `/users` | Получить список пользователей | ✅ |
| 7 | GET | `/users/{user_id}` | Получить пользователя по ID | ✅ |
| 8 | POST | `/users` | Создать нового пользователя | ✅ |
| 9 | PATCH | `/users/{user_id}` | Частично обновить пользователя | ✅ |
| 10 | DELETE | `/users/{user_id}` | Удалить пользователя | ✅ |

### 5.3 Equipment (Оборудование) - CRUD + фильтрация + сортировка

| № | Метод | Endpoint | Описание | Статус |
|---|-------|----------|----------|--------|
| 11 | GET | `/equipment` | Получить список оборудования | ✅ |
| 12 | GET | `/equipment/{equipment_id}` | Получить оборудование по ID | ✅ |
| 13 | POST | `/equipment` | Создать новое оборудование | ✅ |
| 14 | PATCH | `/equipment/{equipment_id}` | Частично обновить оборудование | ✅ |
| 15 | DELETE | `/equipment/{equipment_id}` | Удалить оборудование | ✅ |

### 5.4 Rentals (Аренды) - CRUD

| № | Метод | Endpoint | Описание | Статус |
|---|-------|----------|----------|--------|
| 16 | GET | `/rentals` | Получить список аренд | ✅ |
| 17 | GET | `/rentals/{rental_id}` | Получить аренду по ID | ✅ |
| 18 | POST | `/rentals` | Создать новую аренду | ✅ |
| 19 | PATCH | `/rentals/{rental_id}` | Частично обновить аренду | ✅ |
| 20 | DELETE | `/rentals/{rental_id}` | Удалить аренду | ✅ |

### 5.5 Rental Items (Позиции аренды)

| № | Метод | Endpoint | Описание | Статус |
|---|-------|----------|----------|--------|
| 21 | GET | `/rentals/{rental_id}/items` | Получить позиции аренды | ✅ |
| 22 | POST | `/rentals/{rental_id}/items` | Добавить позицию в аренду | ✅ |

### 5.6 Payments (Платежи)

| № | Метод | Endpoint | Описание | Статус |
|---|-------|----------|----------|--------|
| 23 | GET | `/payments` | Получить список платежей | ✅ |
| 24 | POST | `/payments` | Создать новый платеж | ✅ |

### 5.7 Reviews (Отзывы)

| № | Метод | Endpoint | Описание | Статус |
|---|-------|----------|----------|--------|
| 25 | GET | `/reviews` | Получить список отзывов | ✅ |
| 26 | POST | `/reviews` | Создать новый отзыв | ✅ |

### 5.8 Views (Представления БД)

| № | Метод | Endpoint | Описание | Статус |
|---|-------|----------|----------|--------|
| 27 | GET | `/views/equipment-catalog` | Каталог оборудования (view) | ✅ |
| 28 | GET | `/views/rental-details` | Детализация аренд (view) | ✅ |
| 29 | GET | `/views/client-activity` | Активность клиентов (view) | ✅ |

### 5.9 Reports (Отчеты/Агрегации)

| № | Метод | Endpoint | Описание | Статус |
|---|-------|----------|----------|--------|
| 30 | GET | `/reports/sales-by-category` | Продажи по категориям | ✅ |
| 31 | GET | `/reports/top-customers` | Топ клиентов по тратам | ✅ |
| 32 | GET | `/reports/top-equipment` | Топ оборудования по арендам | ✅ |

### 5.10 Functions (Хранимые функции)

| № | Метод | Endpoint | Описание | Статус |
|---|-------|----------|----------|--------|
| 33 | GET | `/users/{user_id}/rentals-count` | Количество аренд пользователя | ✅ |
| 34 | GET | `/rentals/{rental_id}/total-price` | Общая стоимость аренды | ✅ |

### 5.11 Health Check

| № | Метод | Endpoint | Описание | Статус |
|---|-------|----------|----------|--------|
| 35 | GET | `/` | Корневой endpoint | ✅ |
| 36 | GET | `/health` | Проверка состояния | ✅ |

---

## 6. Детальное описание каждого endpoint

### 6.1 Categories

#### GET /categories
**Описание:** Получение списка всех категорий с поддержкой пагинации.

**Параметры запроса (query):**
- `page` (int, optional, default=1, min=1) - номер страницы
- `limit` (int, optional, default=10, min=1, max=100) - количество записей на странице

**Ответ:** Список объектов CategoryResponse

**Пример ответа:**
```json
[
  {
    "id": 1,
    "name": "Строительное оборудование",
    "description": "Оборудование для строительных работ"
  },
  {
    "id": 2,
    "name": "Садовый инвентарь",
    "description": "Инструменты для сада и огорода"
  }
]
```

---

#### GET /categories/{category_id}
**Описание:** Получение категории по её идентификатору.

**Параметры пути (path):**
- `category_id` (int, required) - ID категории

**Ответ:** Объект CategoryResponse или 404 Not Found

**Коды ответа:**
- 200 - Успешно
- 404 - Категория не найдена

---

#### POST /categories
**Описание:** Создание новой категории.

**Тело запроса (Body):**
```json
{
  "name": "Название категории",
  "description": "Описание категории (опционально)"
}
```

**Ответ:** Созданный объект CategoryResponse

**Коды ответа:**
- 201 - Создано
- 400 - Ошибка валидации

---

#### PUT /categories/{category_id}
**Описание:** Полное обновление (замена) категории.

**Параметры пути:**
- `category_id` (int, required) - ID категории

**Тело запроса:**
```json
{
  "name": "Новое название",
  "description": "Новое описание"
}
```

**Ответ:** Обновленный объект CategoryResponse

**Коды ответа:**
- 200 - Успешно обновлено
- 404 - Категория не найдена

---

#### DELETE /categories/{category_id}
**Описание:** Удаление категории.

**Параметры пути:**
- `category_id` (int, required) - ID категории

**Ответ:** Пустой ответ (204 No Content)

**Коды ответа:**
- 204 - Успешно удалено
- 404 - Категория не найдена

---

### 6.2 Users

#### GET /users
**Описание:** Получение списка пользователей с поддержкой пагинации, фильтрации и сортировки.

**Параметры запроса:**
- `page` (int, optional, default=1, min=1) - номер страницы
- `limit` (int, optional, default=10, min=1, max=100) - количество записей
- `city` (str, optional) - фильтр по городу (частичное совпадение, нечувствительно к регистру)
- `sort` (str, optional) - поле для сортировки (id, first_name, last_name, city и т.д.)
- `order` (str, optional, pattern="^(asc|desc)$") - направление сортировки (asc/desc)

**Примеры запросов:**
```bash
# Все пользователи
GET /users

# Пользователи из Москвы
GET /users?city=Москва

# Пользователи с пагинацией
GET /users?page=2&limit=20

# Пользователи отсортированные по имени (убывание)
GET /users?sort=first_name&order=desc
```

---

#### GET /users/{user_id}
**Описание:** Получение пользователя по ID.

**Ответ:** Объект UserResponse или 404

---

#### POST /users
**Описание:** Создание нового пользователя.

**Тело запроса:**
```json
{
  "first_name": "Иван",
  "last_name": "Иванов",
  "patronymic": "Петрович",
  "login": "ivan_ivanov",
  "password_hash": "hashed_password_here",
  "phone": "+79991234567",
  "city": "Москва"
}
```

**Обязательные поля:** first_name, login, password_hash, phone, city

**Ответ:** Созданный объект UserResponse

**Коды ответа:**
- 201 - Создано
- 400 - Ошибка (дублирование уникального поля и т.д.)
- 422 - Ошибка валидации

---

#### PATCH /users/{user_id}
**Описание:** Частичное обновление пользователя (только переданные поля).

**Тело запроса:**
```json
{
  "first_name": "Новое имя",
  "city": "Новый город"
}
```

**Особенность:** Позволяет обновлять отдельные поля без полной замены объекта.

---

#### DELETE /users/{user_id}
**Описание:** Удаление пользователя.

**Особенность:** Каскадное удаление (CASCADE) - удалятся все связанные записи (аренды, отзывы).

---

### 6.3 Equipment

#### GET /equipment
**Описание:** Получение списка оборудования с фильтрацией и сортировкой.

**Параметры запроса:**
- `page` (int, optional) - номер страницы
- `limit` (int, optional) - количество записей
- `category_id` (int, optional) - фильтр по ID категории
- `owner_id` (int, optional) - фильтр по ID владельца
- `min_price` (float, optional) - минимальная цена за день
- `max_price` (float, optional) - максимальная цена за день
- `sort` (str, optional) - поле для сортировки
- `order` (str, optional) - направление сортировки

**Примеры:**
```bash
# Оборудование определенной категории
GET /equipment?category_id=1

# Оборудование в ценовом диапазоне
GET /equipment?min_price=100&max_price=500

# Оборудование конкретного владельца
GET /equipment?owner_id=5
```

---

#### GET /equipment/{equipment_id}
**Описание:** Получение оборудования по ID.

---

#### POST /equipment
**Описание:** Создание нового оборудования.

**Тело запроса:**
```json
{
  "owner_id": 1,
  "category_id": 2,
  "name": "Бетономешалка",
  "description": "Бетономешалка 180л",
  "price_per_day": 500.00,
  "total_quantity": 5
}
```

**Обязательные поля:** owner_id, category_id, name, price_per_day, total_quantity

---

#### PATCH /equipment/{equipment_id}
**Описание:** Частичное обновление оборудования.

---

#### DELETE /equipment/{equipment_id}
**Описание:** Удаление оборудования.

---

### 6.4 Rentals

#### GET /rentals
**Описание:** Получение списка аренд с фильтрацией.

**Параметры:**
- `page` - номер страницы
- `limit` - количество записей
- `renter_id` - фильтр по ID арендатора
- `status` - фильтр по статусу

---

#### GET /rentals/{rental_id}
**Описание:** Получение аренды по ID.

---

#### POST /rentals
**Описание:** Создание новой аренды.

**Тело запроса:**
```json
{
  "renter_id": 1,
  "start_date": "2024-01-15",
  "end_date": "2024-01-20",
  "status": "Новый"
}
```

---

#### PATCH /rentals/{rental_id}
**Описание:** Частичное обновление аренды.

---

#### DELETE /rentals/{rental_id}
**Описание:** Удаление аренды.

---

### 6.5 Rental Items

#### GET /rentals/{rental_id}/items
**Описание:** Получение всех позиций (товаров) в конкретной аренде.

**Ответ:** Список RentalItemResponse

---

#### POST /rentals/{rental_id}/items
**Описание:** Добавление новой позиции в аренду.

**Тело запроса:**
```json
{
  "equipment_id": 3,
  "quantity": 2,
  "price_at_booking": 500.00
}
```

---

### 6.6 Payments

#### GET /payments
**Описание:** Получение списка платежей с пагинацией.

---

#### POST /payments
**Описание:** Создание нового платежа.

**Тело запроса:**
```json
{
  "rental_id": 1,
  "payment_amount": 2500.00,
  "payment_date": "2024-01-15",
  "status": "Успешно"
}
```

---

### 6.7 Reviews

#### GET /reviews
**Описание:** Получение списка отзывов с возможностью фильтрации по оборудованию.

**Параметры:**
- `skip` - количество записей для пропуска
- `limit` - количество записей
- `equipment_id` - фильтр по ID оборудования

---

#### POST /reviews
**Описание:** Создание нового отзыва.

**Тело запроса:**
```json
{
  "renter_id": 1,
  "equipment_id": 2,
  "rating": 5,
  "review_text": "Отличное оборудование!",
  "created_at": "2024-01-15"
}
```

**Валидация:** rating должен быть от 1 до 5

---

### 6.8 Views

#### GET /views/equipment-catalog
**Описание:** Получение данных из представления каталога оборудования.

**Возвращает:** Объединенные данные оборудования с категориями, владельцами и рейтингами.

---

#### GET /views/rental-details
**Описание:** Получение данных из представления детализации аренд.

**Возвращает:** Информацию о каждой аренде с указанием клиента, товаров и статусов.

---

#### GET /views/client-activity
**Описание:** Получение данных из представления активности клиентов.

**Возвращает:** Статистику по каждому клиенту (всего аренд, потрачено, последняя аренда).

---

### 6.9 Reports

#### GET /reports/sales-by-category
**Описание:** Агрегационный отчет по продажам (арендам) в разрезе категорий.

**Возвращает:**
```json
[
  {
    "category": "Строительное оборудование",
    "count": 15,
    "avg_price": 750.50,
    "total_value": 11257.50
  }
]
```

**Поля:**
- `category` - название категории
- `count` - количество единиц оборудования в категории
- `avg_price` - средняя цена за день
- `total_value` - общая стоимость всего оборудования категории

---

#### GET /reports/top-customers
**Описание:** Отчет по топ-N клиентов по сумме потраченных средств.

**Параметры:**
- `limit` (int, optional, default=10, min=1, max=100) - количество клиентов в отчете

**Возвращает:**
```json
[
  {
    "id": 1,
    "name": "Иван Иванов",
    "rentals": 10,
    "spent": 15000.00
  }
]
```

**Особенность:** Учитываются только успешные платежи (status = "Успешно")

---

#### GET /reports/top-equipment
**Описание:** Отчет по топ-N оборудования по количеству аренд.

**Параметры:**
- `limit` (int, optional, default=10) - количество позиций

**Возвращает:**
```json
[
  {
    "id": 1,
    "name": "Бетономешалка",
    "price": 500.00,
    "rent_count": 25,
    "avg_rating": 4.5
  }
]
```

---

### 6.10 Functions

#### GET /users/{user_id}/rentals-count
**Описание:** Вызов хранимой функции для получения количества аренд пользователя.

**Параметры:**
- `user_id` (int, required) - ID пользователя

**Валидация:**
- ID должен быть положительным числом (>= 1)
- Пользователь должен существовать в базе данных

**Ответ:**
```json
{
  "user_id": 1,
  "rentals_count": 5
}
```

---

#### GET /rentals/{rental_id}/total-price
**Описание:** Вызов хранимой функции для получения общей стоимости аренды.

**Параметры:**
- `rental_id` (int, required) - ID аренды

**Ответ:**
```json
{
  "rental_id": 1,
  "total_price": 2500.00
}
```

---

### 6.11 Health Check

#### GET /
**Описание:** Корневой endpoint для проверки работоспособности API.

**Ответ:**
```json
{
  "message": "Rental Equipment API is running"
}
```

---

#### GET /health
**Описание:** Health check endpoint для мониторинга состояния приложения.

**Ответ:**
```json
{
  "status": "healthy"
}
```

---

## 7. Параметры запросов и фильтрации

### 7.1 Пагинация

Применяется к: `/categories`, `/users`, `/equipment`, `/rentals`, `/payments`, `/reviews`, `/views/*`

| Параметр | Тип | Ограничения | По умолчанию | Описание |
|----------|-----|-------------|--------------|-----------|
| page | int | >= 1 | 1 | Номер страницы |
| limit | int | 1-100 | 10 | Количество записей на странице |

**Формула расчёта:** `skip = (page - 1) * limit`

---

### 7.2 Фильтрация

#### Users
| Параметр | Тип | Описание | Пример |
|----------|-----|-----------|--------|
| city | str | Частичное совпадение (LIKE), case-insensitive | `?city=Москва` |

#### Equipment
| Параметр | Тип | Описание | Пример |
|----------|-----|-----------|--------|
| category_id | int | Точное совпадение | `?category_id=1` |
| owner_id | int | Точное совпадение | `?owner_id=5` |
| min_price | float | >= значение | `?min_price=100` |
| max_price | float | <= значение | `?max_price=500` |

#### Rentals
| Параметр | Тип | Описание | Пример |
|----------|-----|-----------|--------|
| renter_id | int | Точное совпадение | `?renter_id=1` |
| status | str | Точное совпадение | `?status=Активна` |

#### Reviews
| Параметр | Тип | Описание | Пример |
|----------|-----|-----------|--------|
| equipment_id | int | Точное совпадение | `?equipment_id=2` |

---

### 7.3 Сортировка

Применяется к: `/users`, `/equipment`

| Параметр | Тип | Возможные значения | Описание |
|----------|-----|-------------------|-----------|
| sort | str | Название поля модели (id, first_name, last_name, city, price_per_day и т.д.) | Поле для сортировки |
| order | str | asc, desc | Направление сортировки |

**Примеры:**
```bash
# Сортировка пользователей по имени (по возрастанию)
GET /users?sort=first_name&order=asc

# Сортировка оборудования по цене (по убыванию)
GET /equipment?sort=price_per_day&order=desc
```

---

## 8. Коды ответа HTTP

| Код | Название | Описание | Пример использования |
|-----|----------|----------|---------------------|
| **200** | OK | Успешный запрос | GET, PATCH, PUT (успешное выполнение) |
| **201** | Created | Успешное создание ресурса | POST (создание новой записи) |
| **204** | No Content | Успешный запрос без возврата данных | DELETE (удаление) |
| **400** | Bad Request | Неверный запрос (ошибка на уровне приложения) | Нарушение уникальности, ошибки БД |
| **404** | Not Found | Ресурс не найден | Запрос по несуществующему ID |
| **422** | Unprocessable Entity | Ошибка валидации (Pydantic) | Неверный формат данных, нарушение ограничений |
| **500** | Internal Server Error | Внутренняя ошибка сервера | Ошибки при вызове хранимых функций |

---

## 9. Обработка ошибок

### 9.1 Ошибка 404 - Ресурс не найден

**Категории:**
```bash
curl http://localhost:8000/categories/999999
# HTTP 404
{"detail":"Category not found"}
```

**Пользователи:**
```bash
curl http://localhost:8000/users/999999
# HTTP 404
{"detail":"User not found"}
```

**Оборудование:**
```bash
curl http://localhost:8000/equipment/999999
# HTTP 404
{"detail":"Equipment not found"}
```

**Аренды:**
```bash
curl http://localhost:8000/rentals/999999
# HTTP 404
{"detail":"Rental not found"}
```

---

### 9.2 Ошибка 422 - Валидация параметров пагинации

```bash
# page меньше 1
curl "http://localhost:8000/equipment?page=0"
# HTTP 422
{
  "detail": [
    {
      "type": "greater_than_equal",
      "loc": ["query", "page"],
      "msg": "Input should be greater than or equal to 1",
      "input": "0"
    }
  ]
}

# limit больше 100
curl "http://localhost:8000/equipment?limit=200"
# HTTP 422
{
  "detail": [...]
}
```

---

### 9.3 Ошибка 400 - Отрицательный ID в функциях

```bash
# Отрицательный ID пользователя
curl http://localhost:8000/users/-1/rentals-count
# HTTP 400
{"detail":"ID пользователя должен быть положительным числом"}

# Отрицательный ID аренды
curl http://localhost:8000/rentals/-1/total-price
# HTTP 400
{"detail":"ID аренды должен быть положительным числом"}
```

---

### 9.4 Ошибка 404 - Несуществующий ID в функциях

```bash
# Пользователь не найден
curl http://localhost:8000/users/100000000/rentals-count
# HTTP 404
{"detail":"Пользователь с ID=100000000 не найден"}

# Аренда не найдена
curl http://localhost:8000/rentals/100000000/total-price
# HTTP 404
{"detail":"Аренда с ID=100000000 не найдена"}
```

---

### 9.5 Ошибка 422 - Валидация при создании

```bash
# Пустые обязательные поля
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"first_name": "", "login": "", "password_hash": "x"}'

# HTTP 422
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "first_name"],
      "msg": "String should have at least 1 character",
      "input": ""
    },
    {
      "type": "missing",
      "loc": ["body", "phone"],
      "msg": "Field required"
    }
  ]
}
```

---

### 9.6 Ошибка 400 - Дублирование уникального поля

```bash
# Дублирование логина
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"login":"user_1","password_hash":"x","phone":"+79100000020","city":"Москва","first_name":"Test"}'

# HTTP 400 (PostgreSQL error через SQLAlchemy)
{"detail":"Key (login)=(user_1) already exists."}

# Дублирование телефона
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"login":"new_login","password_hash":"x","phone":"+79100000001","city":"Москва","first_name":"Test"}'

# HTTP 400
{"detail":"Key (phone)=(+79100000001) already exists."}
```

---

### 9.7 Ошибка 500 - Ошибка хранимой функции

```bash
# Если функция вызывает исключение
curl http://localhost:8000/users/1/rentals-count

# При ошибке
# HTTP 500
{"detail":"Ошибка при вызове функции: ..."}
```

---

## 10. Валидация данных

Валидация данных реализована с использованием библиотеки **Pydantic** и применяется ко всем входящим данным в запросах POST и PATCH.

### 10.1 Категории (CategoryCreate)

| Поле | Тип | Ограничения | Обязательно |
|------|-----|-------------|-------------|
| name | str | max_length=256 | Да |
| description | str | optional | Нет |

---

### 10.2 Пользователи (UserCreate)

| Поле | Тип | Ограничения | Обязательно |
|------|-----|-------------|-------------|
| first_name | str | max_length=256 | Да |
| last_name | str | max_length=256, optional | Нет |
| patronymic | str | max_length=256, optional | Нет |
| login | str | max_length=256 | Да |
| password_hash | str | max_length=256 | Да |
| phone | str | max_length=20 | Да |
| city | str | max_length=100 | Да |

---

### 10.3 Оборудование (EquipmentCreate)

| Поле | Тип | Ограничения | Обязательно |
|------|-----|-------------|-------------|
| owner_id | int | > 0 | Да |
| category_id | int | > 0 | Да |
| name | str | max_length=256 | Да |
| description | str | optional | Нет |
| price_per_day | Decimal | decimal_places=2 | Да |
| total_quantity | int | >= 0 | Да |

---

### 10.4 Аренда (RentalCreate)

| Поле | Тип | Ограничения | Обязательно |
|------|-----|-------------|-------------|
| renter_id | int | > 0 | Да |
| start_date | date | валидная дата | Да |
| end_date | date | валидная дата | Да |
| status | str | max_length=50, default="Новый" | Нет |

---

### 10.5 Позиция аренды (RentalItemCreate)

| Поле | Тип | Ограничения | Обязательно |
|------|-----|-------------|-------------|
| equipment_id | int | > 0 | Да |
| quantity | int | > 0 | Да |
| price_at_booking | Decimal | decimal_places=2 | Да |

---

### 10.6 Платеж (PaymentCreate)

| Поле | Тип | Ограничения | Обязательно |
|------|-----|-------------|-------------|
| rental_id | int | > 0 | Да |
| payment_amount | Decimal | decimal_places=2 | Да |
| payment_date | date | валидная дата | Да |
| status | str | max_length=50 | Да |

---

### 10.7 Отзыв (ReviewCreate)

| Поле | Тип | Ограничения | Обязательно |
|------|-----|-------------|-------------|
| renter_id | int | > 0 | Да |
| equipment_id | int | > 0 | Да |
| rating | int | 1-5 | Да |
| review_text | str | optional | Нет |
| created_at | date | валидная дата | Да |

---

## 11. Примеры запросов

### 11.1 Получение списка с пагинацией

```bash
# Получить первые 10 пользователей
curl http://localhost:8000/users

# Получить вторую страницу (по 20 записей)
curl "http://localhost:8000/users?page=2&limit=20"
```

### 11.2 Фильтрация

```bash
# Пользователи из Москвы
curl "http://localhost:8000/users?city=Москва"

# Оборудование категории 1 с ценой от 100 до 500
curl "http://localhost:8000/equipment?category_id=1&min_price=100&max_price=500"

# Активные аренды пользователя 1
curl "http://localhost:8000/rentals?renter_id=1&status=Активна"
```

### 11.3 Сортировка

```bash
# Сортировка по имени (убывание)
curl "http://localhost:8000/users?sort=first_name&order=desc"

# Сортировка по цене (возрастание)
curl "http://localhost:8000/equipment?sort=price_per_day&order=asc"
```

### 11.4 Создание ресурсов

```bash
# Создание категории
curl -X POST http://localhost:8000/categories \
  -H "Content-Type: application/json" \
  -d '{"name": "Спортивное оборудование", "description": "Для спортивных мероприятий"}'

# Создание пользователя
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Петр",
    "last_name": "Петров",
    "login": "petr_petrov",
    "password_hash": "hashed_password",
    "phone": "+79991234567",
    "city": "Санкт-Петербург"
  }'

# Создание оборудования
curl -X POST http://localhost:8000/equipment \
  -H "Content-Type: application/json" \
  -d '{
    "owner_id": 1,
    "category_id": 2,
    "name": "Генератор",
    "description": "Бензиновый генератор 5кВт",
    "price_per_day": 800.00,
    "total_quantity": 3
  }'

# Создание аренды
curl -X POST http://localhost:8000/rentals \
  -H "Content-Type: application/json" \
  -d '{
    "renter_id": 1,
    "start_date": "2024-02-01",
    "end_date": "2024-02-07",
    "status": "Новый"
  }'
```

### 11.5 Обновление ресурсов

```bash
# Частичное обновление пользователя
curl -X PATCH http://localhost:8000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"first_name": "Новое имя", "city": "Новосибирск"}'

# Частичное обновление статуса аренды
curl -X PATCH http://localhost:8000/rentals/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "Завершена"}'
```

### 11.6 Удаление ресурсов

```bash
# Удаление категории
curl -X DELETE http://localhost:8000/categories/5

# Удаление пользователя
curl -X DELETE http://localhost:8000/users/10
```

### 11.7 Получение представлений

```bash
# Каталог оборудования
curl http://localhost:8000/views/equipment-catalog

# Детализация аренд
curl http://localhost:8000/views/rental-details

# Активность клиентов
curl http://localhost:8000/views/client-activity
```

### 11.8 Получение отчетов

```bash
# Продажи по категориям
curl http://localhost:8000/reports/sales-by-category

# Топ 5 клиентов
curl "http://localhost:8000/reports/top-customers?limit=5"

# Топ 10 оборудования
curl "http://localhost:8000/reports/top-equipment?limit=10"
```

### 11.9 Вызов функций

```bash
# Количество аренд пользователя
curl http://localhost:8000/users/1/rentals-count

# Общая стоимость аренды
curl http://localhost:8000/rentals/1/total-price
```

---

## 12. Пагинация

### 12.1 Механизм работы

Пагинация реализована с использованием параметров `page` и `limit`:

```python
skip = (page - 1) * limit
query.offset(skip).limit(limit).all()
```

### 12.2 Ограничения

- **page**: минимум 1 (по умолчанию 1)
- **limit**: от 1 до 100 (по умолчанию 10)

### 12.3 Примеры

| Запрос | Результат |
|--------|-----------|
| `GET /users?page=1&limit=10` | Первые 10 записей (0-9) |
| `GET /users?page=2&limit=10` | Записи 10-19 |
| `GET /users?page=3&limit=20` | Записи 40-59 |

---

## 13. Сортировка

### 13.1 Механизм работы

Сортировка реализована с использованием динамического получения атрибутов модели:

```python
col = getattr(Model, sort, Model.id)
query = query.order_by(desc(col) if order == "desc" else asc(col))
```

### 13.2 Поддерживаемые модели и поля

#### Users
- id, first_name, last_name, patronymic, login, phone, city

#### Equipment
- id, owner_id, category_id, name, price_per_day, total_quantity

### 13.3 Примеры

```bash
# Сортировка пользователей по имени (A-Z)
GET /users?sort=first_name&order=asc

# Сортировка оборудования по цене (дорогое сверху)
GET /equipment?sort=price_per_day&order=desc
```

---

## 14. Views (Представления БД)

### 14.1 Назначение

Views (представления) - это виртуальные таблицы в базе данных, которые объединяют данные из нескольких таблиц. Они были созданы в лабораторной работе №2.

### 14.2 Доступ к Views через API

API предоставляет endpoints для получения данных из всех трех представлений:
- `/views/equipment-catalog` - каталог оборудования
- `/views/rental-details` - детализация аренд
- `/views/client-activity` - активность клиентов

### 14.3 Особенности реализации

Данные из views возвращаются в виде словаря (dict), а не объекта модели:

```python
return [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in results]
```

---

## 15. Агрегационные отчеты

### 15.1 Отчет по категориям (`/reports/sales-by-category`)

**Запрос:**
```python
db.query(
    Category.name,
    func.count(Equipment.id).label("equipment_count"),
    func.avg(Equipment.price_per_day).label("avg_price"),
    func.sum(Equipment.price_per_day * Equipment.total_quantity).label("total_value")
).join(Equipment).group_by(Category.id, Category.name).all()
```

**Результат:**
```json
[
  {
    "category": "Строительное оборудование",
    "count": 15,
    "avg_price": 750.50,
    "total_value": 11257.50
  }
]
```

---

### 15.2 Топ клиентов (`/reports/top-customers`)

**Запрос:**
```python
db.query(
    User.id, User.first_name, User.last_name,
    func.count(Rental.id).label("rental_count"),
    func.sum(Payment.payment_amount).label("total_spent")
).join(Rental, User.id == Rental.renter_id).join(
    Payment, Rental.id == Payment.rental_id
).filter(Payment.status == "Успешно").group_by(...).order_by(desc("total_spent"))
```

**Особенности:**
- Учитываются только платежи со статусом "Успешно"
- Сортировка по убыванию суммы

---

### 15.3 Топ оборудования (`/reports/top-equipment`)

**Запрос:**
```python
db.query(
    Equipment.id, Equipment.name, Equipment.price_per_day,
    func.count(RentalItem.equipment_id).label("rent_count"),
    func.avg(Review.rating).label("avg_rating")
).outerjoin(RentalItem).outerjoin(Review).group_by(...)
```

**Особенности:**
- Используется LEFT JOIN для оборудования, которое никогда не арендовалось
- Средний рейтинг может быть NULL для оборудования без отзывов

---

## 16. Хранимые функции

### 16.1 Обзор

Хранимые функции были созданы в лабораторной работе №3 и вызываются через API с использованием SQL-функции `text()` из SQLAlchemy.

### 16.2 Функция get_total_rentals_by_userId

**Вызов из Python:**
```python
result = db.execute(
    text("SELECT get_total_rentals_by_userId(:user_id)"),
    {"user_id": user_id}
).fetchone()
```

**Валидация:**
1. Проверка, что ID >= 1
2. Проверка существования пользователя
3. Вызов функции и возврат результата

---

### 16.3 Функция get_rental_total_price

**Вызов из Python:**
```python
result = db.execute(
    text("SELECT get_rental_total_price(:rental_id)"),
    {"rental_id": rental_id}
).fetchone()
```

**Валидация:**
1. Проверка, что ID >= 1
2. Проверка существования аренды
3. Вызов функции и возврат результата

---

## 17. Вопросы для защиты

### 17.1 Теоретические вопросы

1. **Что такое RESTful API?**
   - REST (Representational State Transfer) - архитектурный стиль для проектирования сетевых приложений
   - Использует HTTP методы (GET, POST, PUT, PATCH, DELETE) для операций CRUD
   - Основаан на ресурсах (сущностях), а не на действиях

2. **Какие HTTP методы используются в API?**
   - GET - получение данных
   - POST - создание новых ресурсов
   - PUT - полное обновление ресурса
   - PATCH - частичное обновление ресурса
   - DELETE - удаление ресурса

3. **Что такое CRUD?**
   - Create - создание
   - Read - чтение
   - Update - обновление
   - Delete - удаление

4. **Для чего используется FastAPI?**
   - FastAPI - современный веб-фреймворк для создания API на Python
   - Автоматическая генерация документации (Swagger UI, ReDoc)
   - Встроенная валидация данных через Pydantic
   - Асинхронная поддержка (async/await)
   - Высокая производительность

5. **Для чего используется SQLAlchemy?**
   - ORM (Object-Relational Mapping) для работы с базой данных
   - Позволяет работать с БД через объекты Python
   - Создание моделей данных
   - Выполнение запросов

6. **Для чего используется Pydantic?**
   - Валидация данных
   - Сериализация/десериализация данных
   - Типизация данных
   - Автоматическая генерация схем для документации

7. **Что такое пагинация и зачем она нужна?**
   - Разделение большого объема данных на страницы
   - Уменьшение нагрузки на сервер и клиент
   - Улучшение производительности
   - Параметры page (номер страницы) и limit (размер страницы)

8. **Что такое фильтрация?**
   - Отбор данных по определенным критериям
   - Параметры запроса для выборки нужных записей
   - Пример: `?city=Москва`, `?category_id=1`, `?min_price=100`

9. **Что такое сортировка?**
   - Упорядочивание результатов по определенному полю
   - Параметры sort (поле) и order (направление)
   - Пример: `?sort=price_per_day&order=desc`

10. **Что такое Views (представления) в базе данных?**
    - Виртуальные таблицы, хранящие результаты запроса
    - Объединяют данные из нескольких таблиц
    - Упрощают часто используемые запросы
    - В данном проекте: v_equipment_catalog, v_rental_details, v_client_activity

11. **Что такое агрегационные функции?**
    - Функции для расчета статистических показателей
    - COUNT, SUM, AVG, MIN, MAX
    - В проекте используются для отчетов

12. **Что такое хранимые функции?**
    - Функции, хранящиеся в базе данных
    - Выполняются на стороне СУБД
    - В проекте: get_total_rentals_by_userId, get_rental_total_price

13. **Какие коды ответа HTTP используются в проекте?**
    - 200 - OK
    - 201 - Created
    - 204 - No Content
    - 400 - Bad Request
    - 404 - Not Found
    - 422 - Unprocessable Entity
    - 500 - Internal Server Error

14. **Что такое PATCH и чем он отличается от PUT?**
    - PUT - полное обновление (замена всего объекта)
    - PATCH - частичное обновление (только указанные поля)

15. **Зачем нужна валидация данных?**
    - Защита от некорректных данных
    - Предотвращение ошибок в базе данных
    - Обеспечение целостности данных

---

### 17.2 Практические вопросы

1. **Как запустить приложение?**
   ```bash
   cd /home/ares/Databases/labs/6
   source venv/bin/activate
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

2. **Как получить документацию API?**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

3. **Как получить список пользователей?**
   ```bash
   curl http://localhost:8000/users
   ```

4. **Как создать нового пользователя?**
   ```bash
   curl -X POST http://localhost:8000/users \
     -H "Content-Type: application/json" \
     -d '{"first_name":"Иван","login":"ivan","password_hash":"xxx","phone":"+7999","city":"Москва"}'
   ```

5. **Как отфильтровать оборудование по категории?**
   ```bash
   curl http://localhost:8000/equipment?category_id=1
   ```

6. **Как отсортировать пользователей по имени?**
   ```bash
   curl "http://localhost:8000/users?sort=first_name&order=asc"
   ```

7. **Как получить вторую страницу пользователей?**
   ```bash
   curl "http://localhost:8000/users?page=2&limit=20"
   ```

8. **Как получить отчет по категориям?**
   ```bash
   curl http://localhost:8000/reports/sales-by-category
   ```

9. **Как вызвать функцию подсчета аренд пользователя?**
   ```bash
   curl http://localhost:8000/users/1/rentals-count
   ```

10. **Как обрабатываются ошибки 404?**
    - При запросе несуществующего ресурса возвращается JSON с полем detail
    - Пример: `{"detail":"User not found"}`

11. **Какие поля обязательны при создании пользователя?**
    - first_name, login, password_hash, phone, city

12. **Какие поля обязательны при создании оборудования?**
    - owner_id, category_id, name, price_per_day, total_quantity

13. **Что произойдет при попытке удалить категорию с оборудованием?**
    - Вернется ошибка 500 (так как используется RESTRICT)

14. **Как работает каскадное удаление?**
    - При удалении пользователя удаляются все его аренды, отзывы, оборудование
    - Реализуется через FOREIGN KEY с ON DELETE CASCADE

15. **Какой статус по умолчанию у новой аренды?**
    - "Новый"

16. **Какой диапазон значений для рейтинга отзыва?**
    - От 1 до 5

17. **Что возвращает endpoint /health?**
    - `{"status":"healthy"}`

---

### 17.3 Вопросы по базе данных

1. **Какие таблицы используются в проекте?**
   - categories, users, equipment, rentals, rental_items, payments, reviews

2. **Какие связи между таблицами?**
   - one-to-many (User -> Equipment, User -> Rentals, Category -> Equipment)
   - many-to-many через rental_items (Rental <-> Equipment)
   - one-to-many (Rental -> Payments, Rental -> RentalItems)

3. **Какие представления (views) используются?**
   - v_equipment_catalog, v_rental_details, v_client_activity

4. **Какие хранимые функции используются?**
   - get_total_rentals_by_userId(user_id)
   - get_rental_total_price(rental_id)

---

### 17.4 Вопросы по архитектуре

1. **Какая структура проекта?**
   - main.py - endpoints и бизнес-логика
   - models.py - SQLAlchemy модели
   - schemas.py - Pydantic схемы валидации

2. **Какие зависимости используются?**
   - fastapi, uvicorn, sqlalchemy, psycopg2-binary, pydantic

3. **Какой паттерн используется?**
   - MVC-подобный паттерн с разделением на Model, View (schemas), Controller (main)

---

### 17.5 Вопросы по безопасности

1. **Как обрабатываются ошибки валидации?**
   - Pydantic автоматически проверяет данные и возвращает 422 при ошибках

2. **Как обрабатываются ошибки базы данных?**
   - SQLAlchemy транслирует ошибки PostgreSQL в HTTP 400

3. **Какие меры защиты от SQL-инъекций?**
   - SQLAlchemy использует параметризованные запросы (защита от инъекций встроена)

---

## Дополнительная информация

### Структура файлов проекта

```
labs/6/
├── main.py          # FastAPI приложение (489 строк)
├── models.py        # SQLAlchemy модели (150 строк)
├── schemas.py       # Pydantic схемы (165 строк)
├── requirements.txt # Зависимости
├── venv/           # Виртуальное окружение
└── Лабораторная работа №6.pdf  # Задание
```

### Ключевые особенности реализации

1. **Полный CRUD** для всех сущностей
2. **Пагинация** для всех списковых endpointов
3. **Фильтрация** по различным полям
4. **Сортировка** с выбором направления
5. **Валидация** через Pydantic
6. **Обработка ошибок** с понятными сообщениями
7. **Views** для объединенных данных
8. **Агрегационные отчеты**
9. **Вызов хранимых функций**
10. **Автоматическая документация** Swagger UI и ReDoc

---

**Дата создания:** 2024
**Версия API:** 1.0.0
**Автор:** Лабораторная работа №6