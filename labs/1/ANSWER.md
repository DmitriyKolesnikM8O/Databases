## ВАРИАНТ 13: Сервис аренды спортивного инвентаря ##
Платформа для аренды велосипедов, лыж, снаряжения для кемпинга и т.д. Владельцы инвентаря выставляют его в аренду. Арендаторы могут искать, бронировать и оплачивать аренду на определенные даты.

### Сущности ###

1. Пользователь
    - id - Primary Key 
    - Имя
    - Фамилия
    - Отчество
    - Логин
    - Пароль
    - телефон
    - город
2. Инвентарь
    - id - Primary Key
    - название
    - описание
    - id_владельца - Foreign Key
    - количество
    - цена_аренды
3. Заказ аренды
    - id - Primary Key
    - дата_начала
    - дата_конца
    - id_владельца - Foreign Key
    - общая_стоимость (!Нарушает 3NF!)
    - статус
4. Позиция аренды
    - id аренды - Foreign Key
    - id инвентаря - Foreign Key
  Primary Key = id аренды + id инвентаря
    - количество
    - цена_за_день_на_момент_заказа
5. Категория
    - id - Primary Key
    - название
    - описание
6. Отзыв
    - id - Primary Key
    - id_арендатора - Foreign Key
    - id_инвентаря - Foreign Key
    - оценка
    - текст
    - дата_создания
7. Платеж
    - id - Primary Key
    - id_аренды - Foreign Key
    - дата_оплаты
    - статус
    - сумма_оплаты
  

**Как это вообще должно работать:** есть платформа. Чел регается, как владелец оборудования. В аккаунте он выставляет все свое оборудование, которое у него есть. Затем другой чел регается, как арендатор. Арендатор выбирает из представленного оборудования, бронирует его и оплачивает аренду. Есть отдельно карточка аренды, в которой прописаны все параметры: че арендовано, на сколько арендовано, кем, у кого, за сколько.

### Обоснование выбранных типов и структуры таблицы ### 

- Первая нормальная форма (1NF): Все атрибуты атомарны. Список арендованных товаров не хранится в одной ячейке таблицы Rentals. Вместо этого - отдельная таблица Rental_Items.
- Вторая нормальная форма (2NF): Все неключевые поля зависят от полного первичного ключа. Например, название категории зависит только от category_id, поэтому оно вынесено в отдельную таблицу Categories, а не дублируется для каждого товара.
- Третья нормальная форма (3NF): В таблицах отсутствуют транзитивные зависимости. Например, не хранится поле «Доступное количество» в таблице Equipment, так как оно является вычисляемым (Общее кол-во - Активные аренды). 
- Отношение «Многие-ко-Многим»: Связь между Инвентарем и Заказом реализована через промежуточную таблицу Rental_Items. Это позволяет одному пользователю взять в аренду сразу несколько разных предметов в рамках одного чека.


- SERIAL / INTEGER: Использованы для первичных (PK) и внешних (FK) ключей. 
- VARCHAR(256) / VARCHAR(20): Для ФИО и логинов выбран предел в 256 символов. Для номера телефона выбран лимит 20 символов, что покрывает международные форматы. 
- NUMERIC(10, 2): Выбран для полей стоимости и платежей.
- DATE / TIMESTAMP: Использованы для дат аренды и отзывов для обеспечения корректной работы с календарем и возможности фильтрации по периодам.
- TEXT: Использован для описаний и текстов отзывов, так как их длина может быть произвольной и заранее неизвестна.


- Ограничение UNIQUE: Наложено на поля login и phone. Это гарантирует уникальность аккаунтов
- Ограничение NOT NULL: Проставлено для всех важных полей.
- Ограничение CHECK:
  - Для количества товара (quantity > 0) — защищает от ввода ошибочных отрицательных значений.
  - Для рейтинга (rating BETWEEN 1 AND 5) — ограничивает шкалу оценки в рамках заданной бизнес-логики.
  - Для дат аренды (end_date >= start_date) — гарантирует, что дата возврата не может быть раньше даты выдачи.
- Историчность цен (price_at_booking): В таблице Rental_Items фиксируется цена товара на момент заказа. Зачем: если владелец завтра изменит цену на свои лыжи, сумма уже совершенных ранее сделок в базе не изменится.
- CASCADE DELETE: Для внешних ключей настроено каскадное удаление. Если пользователь удаляет свой аккаунт, система автоматически удалит связанные с ним профили. 


### ER-диаграмма ###

@startuml
hide circle
skinparam linetype ortho

entity "Пользователь (User)" as user {
  * id : number <<generated>>
  --
  имя : varchar(256) not null
  фамилия : varchar(256)
  отчество : varchar(256)
  логин : varchar(256) unique not null
  пароль : varchar(256) not null
  телефон : varchar(20) unique not null
  город : varchar(100) not null
}

entity "Инвентарь (Equipment)" as equipment {
  * id : number <<generated>>
  --
  * id_владельца : number <<FK>>
  * id_категории : number <<FK>>
  название : varchar(256) not null
  описание : text
  цена_в_день : number not null
  количество_всего : number not null
}

entity "Заказ аренды (Rental)" as rental {
  * id : number <<generated>>
  --
  * id_арендатора : number <<FK>>
  дата_начала : date not null
  дата_конца : date not null
  общая_стоимость : number not null
  статус : varchar(50) not null
}

entity "Позиция аренды (Rental_Item)" as rental_item {
  * id_аренды : number <<FK, PK>>
  * id_инвентаря : number <<FK, PK>>
  --
  количество : number not null
  цена_за_день_на_момент_заказа : number not null
}

entity "Категория (Category)" as category {
  * id : number <<generated>>
  --
  название : varchar(256) unique not null
  описание : text
}

entity "Отзыв (Review)" as review {
  * id : number <<generated>>
  --
  * id_арендатора : number <<FK>> not null
  * id_инвентаря : number <<FK>> not null
  оценка : number not null
  текст : text
  дата_создания : date not null
}

entity "Платеж (Payment)" as payment {
  * id : number <<generated>>
  --
  id_аренды : number <<FK>> not null
  дата_оплаты : date not null
  статус : varchar (50) not null
  сумма_оплаты : number not null
}

user ||--o{ equipment : "Сдает (Владелец)"

user ||--o{ rental : "Берет (Арендатор)"

rental ||--|{ rental_item : "Содержит"

equipment ||--o{ rental_item : "Участвует в"

category ||--o{ equipment : "Включает"

user ||--o{ review : "Пишет"

equipment ||--o{ review : "Оценен"

rental ||--|{ payment : "Оплачивается"



@enduml


### DDL-Скрипт ###

```sql
CREATE TABLE categories (
  id SERIAL PRIMARY KEY,
  name VARCHAR(256) UNIQUE NOT NULL,
  description TEXT
);

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  first_name VARCHAR(256) NOT NULL,
  last_name VARCHAR(256),
  patronymic VARCHAR(256),
  login VARCHAR(256) UNIQUE NOT NULL,
  password_hash VARCHAR(256) NOT NULL,
  phone VARCHAR(20) UNIQUE NOT NULL,
  city VARCHAR(100) NOT NULL
);

CREATE TABLE equipment (
  id SERIAL PRIMARY KEY,
  owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
  name VARCHAR(256) NOT NULL,
  description TEXT,
  price_per_day NUMERIC(10, 2) NOT NULL, 
  total_quantity INTEGER NOT NULL CHECK (total_quantity >= 0) 
);

CREATE TABLE rentals (
  id SERIAL PRIMARY KEY,
  renter_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  total_amount NUMERIC(10, 2) NOT NULL,
  status VARCHAR(50) NOT NULL,
  CHECK (end_date >= start_date) 
);

CREATE TABLE rental_items (
  rental_id INTEGER NOT NULL REFERENCES rentals(id) ON DELETE CASCADE,
  equipment_id INTEGER NOT NULL REFERENCES equipment(id) ON DELETE CASCADE,
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  price_at_booking NUMERIC(10, 2) NOT NULL,
  PRIMARY KEY (rental_id, equipment_id) 
);

CREATE TABLE payments (
  id SERIAL PRIMARY KEY,
  rental_id INTEGER NOT NULL REFERENCES rentals(id) ON DELETE CASCADE,
  payment_amount NUMERIC(10, 2) NOT NULL CHECK (payment_amount > 0),
  payment_date DATE NOT NULL,
  status VARCHAR(50) NOT NULL
);

CREATE TABLE reviews (
  id SERIAL PRIMARY KEY,
  renter_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  equipment_id INTEGER NOT NULL REFERENCES equipment(id) ON DELETE CASCADE,
  rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5), 
  review_text TEXT,
  created_at DATE NOT NULL DEFAULT CURRENT_DATE
);
```

### Как проверялся скрипт ###
через команду: "sqlite3 test_is_script_correct.db < dll.sql", а затем "sqlite3 test_is_script_correct.db" и в самой оболочке .tables и .schema users - все корректно
















