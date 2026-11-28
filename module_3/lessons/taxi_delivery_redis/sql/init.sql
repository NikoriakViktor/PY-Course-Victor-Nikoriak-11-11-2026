-- PostgreSQL = ДЖЕРЕЛО ПРАВДИ (урок 30). Redis (урок 31) стоїть поруч і тримає «гаряче».
CREATE TABLE restaurants (
    id        INTEGER PRIMARY KEY,
    name      TEXT NOT NULL,
    cuisine   TEXT NOT NULL,
    district  TEXT NOT NULL,
    lat       DOUBLE PRECISION NOT NULL,
    lon       DOUBLE PRECISION NOT NULL
);

CREATE TABLE menu_items (
    id            SERIAL PRIMARY KEY,
    restaurant_id INTEGER NOT NULL REFERENCES restaurants(id),
    name          TEXT NOT NULL,
    price         NUMERIC(8,2) NOT NULL CHECK (price > 0)
);

CREATE TABLE couriers (
    id   TEXT PRIMARY KEY,
    name TEXT NOT NULL
);

-- Сюди потрапляє ЛИШЕ завершене замовлення: поки доставка триває, воно живе в Redis.
CREATE TABLE orders (
    id            BIGINT PRIMARY KEY,
    customer      TEXT NOT NULL,
    restaurant_id INTEGER NOT NULL REFERENCES restaurants(id),
    courier_id    TEXT REFERENCES couriers(id),
    items         JSONB NOT NULL,
    total         NUMERIC(8,2) NOT NULL,
    fee           NUMERIC(8,2) NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL,
    delivered_at  TIMESTAMPTZ NOT NULL,
    lat           DOUBLE PRECISION NOT NULL,
    lon           DOUBLE PRECISION NOT NULL
);

INSERT INTO restaurants (id, name, cuisine, district, lat, lon) VALUES
 (1, 'Піца Поділ',        'Піца',   'Поділ',    50.4680, 30.5160),
 (2, 'Суші Оболонь',      'Суші',   'Оболонь',  50.5010, 30.4980),
 (3, 'Борщ на Печерську', 'Борщ',   'Печерськ', 50.4270, 30.5380),
 (4, 'Бургер Дарниця',    'Бургер', 'Дарниця',  50.4560, 30.6310),
 (5, 'Вега Святошин',     'Вега',   'Святошин', 50.4580, 30.3650),
 (6, 'Борщ Голосіїв',     'Борщ',   'Голосіїв', 50.3870, 30.5100);

INSERT INTO menu_items (restaurant_id, name, price) VALUES
 (1,'Маргарита',180),(1,'Пепероні',220),(1,'Чотири сири',240),(1,'Лимонад',60),
 (2,'Філадельфія',260),(2,'Каліфорнія',230),(2,'Місо-суп',90),(2,'Зелений чай',50),
 (3,'Борщ з пампушками',120),(3,'Котлета по-київськи',190),(3,'Вареники з вишнею',120),(3,'Узвар',45),
 (4,'Козацький бургер',170),(4,'Чізбургер',150),(4,'Картопля фрі',70),(4,'Мілкшейк',90),
 (5,'Боул з кіноа',210),(5,'Фалафель',130),(5,'Крем-суп із гарбуза',100),(5,'Смузі',85),
 (6,'Борщ зелений',115),(6,'Деруни зі сметаною',105),(6,'Голубці',150),(6,'Кисіль',40);

INSERT INTO couriers (id, name) VALUES
 ('c1','Олег'),('c2','Марія'),('c3','Андрій'),('c4','Тарас'),
 ('c5','Оксана'),('c6','Богдан'),('c7','Ірина'),('c8','Максим');
