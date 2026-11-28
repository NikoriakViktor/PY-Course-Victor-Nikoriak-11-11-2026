# 🍕🚕 Смачно + Таксі на Redis — підсумковий проєкт

Один великий приклад, що об'єднує **урок 30 (PostgreSQL)** і **урок 31 (Redis)**: диспетчерська доставки їжі кур'єрами по Києву.

> **PostgreSQL — джерело правди** (ресторани, меню, завершені замовлення). **Redis — «гаряче»**: усе, що змінюється щосекунди й має жити швидко.

> 🗺️ **Загальна картина:** [`ARCHITECTURE.md`](ARCHITECTURE.md) — схема процесів, шлях одного замовлення, де живе кожна сутність, які функції шлють які команди і чому так. Інтерактивно, з анімаціями й пісочницею Redis: [`module_3/bonus/Бази даних — загальна картина.html`](../../bonus/Бази%20даних%20—%20загальна%20картина.html).

## Запуск

**0. Запусти Docker Desktop** і дочекайся напису «Engine running» унизу зліва. Перевірка в терміналі: `docker version` має показати і `Client`, і `Server`.

**1. Відкрий термінал у корені репозиторію курсу.** У PyCharm — вкладка **Terminal** унизу: вона відкривається саме в корені проєкту. Або PowerShell чи cmd і `cd` до папки, куди ти склонував курс.

**2. Перейди в папку цього проєкту** — туди, де лежить `docker-compose.yml`:

```bash
cd module_3/lessons/taxi_delivery_redis
```

Перевір, що ти на місці: `dir` (Windows) або `ls` (macOS, Linux) має показати `docker-compose.yml`, `Dockerfile`, `app` і `sql`.

**3. Запусти:**

```bash
docker compose up --build
```

Перший запуск збирає образ і завантажує PostgreSQL та Redis — це кілька хвилин. Термінал залишиться зайнятим логами сервісів: так і має бути, не закривай його. Зупинка — `Ctrl+C`, потім `docker compose down` (`-v` — разом з даними) у тій самій папці.

> **Помилка `no configuration file provided: not found`** означає, що ти не в тій папці: `docker compose` шукає `docker-compose.yml` лише в поточній. Повернись до кроку 2.
>
> **Не хочеш переходити в папку?** З кореня репозиторію можна вказати файл явно:
> `docker compose -f module_3/lessons/taxi_delivery_redis/docker-compose.yml up --build`
>
> **Помилка `port is already allocated`** — порт 5434, 6390, 8060 чи 8100 уже зайнятий іншим контейнером або програмою (часто — іншим PostgreSQL). `docker ps` покаже, хто його тримає. Зупини той контейнер або зміни лівий номер у `ports:` у `docker-compose.yml`, наприклад `"5435:5432"`, і перезапусти: `docker compose down`, потім `docker compose up --build`.
>
> **Сторінка не відкривається (`ERR_EMPTY_RESPONSE`), а в логах `PostgreSQL ще недоступний` / `PostgreSQL недоступний`** — сервіси не бачать базу. Найчастіше попередній запуск упав на зайнятому порту і контейнер `postgres` лишився без мережі. Лікується так само: `docker compose down`, потім `docker compose up --build`.

Коли все піднялось:

| Що | Адреса |
|---|---|
| 🗺️ Дашборд диспетчерської | http://localhost:8060 |
| 📘 API (Swagger) | http://localhost:8100/docs |
| ⚡ Redis | `redis-cli -p 6390` |
| 🐘 PostgreSQL | `psql postgresql://taxi:taxi@localhost:5434/smachno` або `docker compose exec postgres psql -U taxi smachno` |

Через ~10 секунд на мапі з'являться замовлення та кур'єри в дорозі. Команди `redis-cli` і `docker compose run/kill` із завдань нижче теж виконуй у цій папці.

## Логи: що відбувається всередині

`docker compose up` друкує логи всіх сервісів разом. Для заняття зручніше відкрити **другий термінал у цій самій папці** і дивитись вибірково:

```bash
docker compose logs -f dispatcher simulator generator api   # черга і задачі: шлях кожного замовлення
docker compose logs -f redis-monitor                         # кожна команда Redis і ХТО її надіслав
docker compose logs -f postgres                              # кожен SQL-запит і ХТО його виконав
docker compose logs -f dispatcher                            # лише черга (зручно для завдань 2 і 3)
```

Кожен рядок сервісу починається з часу і тегу:

| Тег | Що означає |
|---|---|
| `TASK` | крок бізнес-процесу: замовлення створено, кур'єра призначено, доставлено |
| `QUEUE` | черга: `XADD`, `XREADGROUP`, `XACK`, pending після падіння, відкладений повтор (`orders:waiting`) |
| `REDIS` | інші команди Redis і їхній результат: кеш HIT/MISS, `INCR`, `GEOSEARCH`, `SREM`, `MULTI/EXEC` |
| `PG` | PostgreSQL: що читаємо з «джерела правди» і що записуємо назавжди |
| `EVENT` | подія для дашборду: `PUBLISH` (скільки підписників почули) + `LPUSH` у стрічку |
| `WARN` | щось пішло не так, але сервіс працює далі |

Так виглядає одне замовлення від клієнта до кур'єра:

```
generator-1   09:33:18  REDIS  INCR ratelimit:client-4 → 1 з 3 за хвилину
generator-1   09:33:18  REDIS  GET cache:menu:5 → MISS (кешу немає) → іду в PostgreSQL
generator-1   09:33:18  PG     SELECT menu_items WHERE restaurant_id=5 → страв у меню: 4
generator-1   09:33:18  REDIS  SET cache:menu:5 EX 60 → кеш на 60 с (разом 8.6 мс)
generator-1   09:33:18  TASK   замовлення #1 від client-4: 1 поз., 200 грн
generator-1   09:33:18  QUEUE  XADD orders:new → 1795858398626-0  (#1 чекає на диспетчера)
dispatcher-1  09:33:18  QUEUE  XREADGROUP dispatchers dispatcher-1 ... > → нових повідомлень: 1 — 1795858398626-0 (#1)
dispatcher-1  09:33:18  REDIS  GEOSEARCH couriers:geo біля «Вега Святошин» → c1 5.8 км, c5 6.1 км, … · вільні: c1, c2, …
dispatcher-1  09:33:18  REDIS  SREM couriers:free c1 → 1 (кур'єр наш, ніхто інший його вже не візьме)
dispatcher-1  09:33:18  TASK   #1 → кур'єр c1 (Олег), 5.8 км до ресторану
dispatcher-1  09:33:18  QUEUE  XACK orders:new dispatchers 1795858398626-0 → 1 (оброблено, з pending прибрано)
simulator-1   09:33:40  TASK   #1: кур'єр c1 у ресторані, забрав їжу → їде до клієнта
simulator-1   09:34:02  TASK   #1 доставлено кур'єром c1 · 200 грн
simulator-1   09:34:02  PG     INSERT INTO orders #1 (200.0 грн) — замовлення збережено назавжди
```

А так те саме бачить сам Redis (`redis-monitor`):

```
generator   ▶ INCRBY order:seq 1
generator   ▶ MULTI
generator   ▶ HSET order:8 id 8 customer client-24 restaurant_id 4 items [...]
generator   ▶ XADD orders:new * order_id 8
generator   ▶ ZADD orders:active 1795858443.86 8
generator   ▶ EXEC
generator   ▶ PUBLISH events:orders {"order_id": 8, "status": "new", ...}
```

Більше або менше деталей — змінні середовища перед запуском (у PowerShell: `$env:LOG_LEVEL="DEBUG"`, у bash: `LOG_LEVEL=DEBUG docker compose up`):

- `LOG_LEVEL=DEBUG` — ще й кожен крок кур'єра (`GEOADD`) і кожне пусте опитування черги;
- `MONITOR_ALL=1` — `redis-monitor` покаже геть усі команди, включно з дашбордом, що читає Redis щосекунди.

> `MONITOR` сповільнює Redis: кожна команда ще й пересилається монітору. Це інструмент для навчання й відладки, на бойовому сервері його не тримають увімкненим.

## Як це працює

```
клієнт ──POST /orders──▶ API ──▶ rate limit ─▶ меню (кеш → PostgreSQL) ─▶ HASH order:<id>
                                                                          └▶ STREAM orders:new
                                                                                  │
 dispatcher ◀── XREADGROUP ◀────────────────────────────────────────────────────┘
     │  GEOSEARCH couriers:geo  → найближчі кур'єри
     │  SREM couriers:free      → атомарно «захопили» вільного
     ▼
 simulator: кур'єр їде (GEOADD щосекунди) → ресторан → клієнт → delivered
     │  ZINCRBY рейтинг · INCR лічильник · PUBLISH подія
     ▼
 PostgreSQL: INSERT INTO orders ...   (замовлення «осіло» назавжди)

 dashboard / GET /events  ◀── читають Redis щосекунди / слухають Pub/Sub
```

## Карта Redis: що де лежить і чому

| Структура | Ключ | Навіщо | Урок 31 |
|---|---|---|---|
| STRING + TTL | `cache:menu:<id>` | кеш меню, cache-aside, живе 60 с | розд. 3, 9 |
| STRING (INCR) | `order:seq`, `stats:*` | id замовлень, лічильники без гонитви | розд. 2 |
| STRING + TTL | `ratelimit:<client>` | не більше 3 замовлень/хв | розд. 15 |
| HASH | `order:<id>`, `courier:<id>`, `restaurant:<id>` | картки сутностей | розд. 5 |
| SET | `couriers:free`, `couriers:all` | вільні кур'єри; `SREM` = атомарний захват | розд. 6 |
| HyperLogLog | `stats:customers:unique` | унікальні клієнти на 12 КБ | розд. 6 |
| ZSET | `orders:active`, `orders:waiting`, `lb:*` | активні замовлення, повтор за часом, рейтинги | розд. 7 |
| LIST | `events:log` | остання стрічка подій | розд. 4 |
| PUB/SUB | `events:orders` | live-повідомлення (дашборд, SSE) | розд. 11 |
| STREAM + group | `orders:new` | надійна черга замовлень для диспетчерів | розд. 10 (наступний рівень) |
| GEO | `couriers:geo`, `restaurants:geo` | «хто найближче?» | — |

Усі назви ключів — в одному файлі [`app/config.py`](app/config.py).

## Файли

| Файл | Роль |
|---|---|
| `sql/init.sql` | схема й дані PostgreSQL |
| `ARCHITECTURE.md` | схема, сутності, функція → команди → ключі, «чому так» |
| `app/config.py` | налаштування і **усі ключі Redis** |
| `app/log.py` | формат логів і теги `TASK` / `QUEUE` / `REDIS` / `PG` / `EVENT` |
| `app/redis_monitor.py` | `MONITOR`: кожна команда Redis з іменем сервісу |
| `app/db.py` | SQL-функції (параметри `%s`, а не f-рядки) |
| `app/menu.py` | **cache-aside** + інвалідація |
| `app/orders.py` | створення замовлення, rate limit, події |
| `app/dispatcher.py` | Stream → GEO → призначення кур'єра |
| `app/simulator.py` | рух кур'єрів, завершення доставки |
| `app/generator.py` | «клієнти», що самі замовляють |
| `app/api.py` | FastAPI |
| `app/dashboard.py` | Dash: мапа, KPI, рейтинг, стрічка |

## Спробуй у `redis-cli -p 6390`

```
GEOSEARCH couriers:geo FROMLONLAT 30.52 50.45 BYRADIUS 5 km ASC WITHDIST
SMEMBERS couriers:free
ZREVRANGE lb:couriers:deliveries 0 -1 WITHSCORES
XINFO GROUPS orders:new
XPENDING orders:new dispatchers
TTL cache:menu:1
PFCOUNT stats:customers:unique
SUBSCRIBE events:orders
```

## Завдання для студентів

1. **Кеш.** Відкрий `GET /restaurants/1/menu` двічі: `source` став `cache`, а час упав. Поміняй ціну в PostgreSQL — коли її побачить клієнт? Виклич `DELETE /restaurants/1/menu/cache` і поясни різницю.
2. **Два диспетчери.** Запусти другого: `docker compose run -d -e DISPATCHER_NAME=d2 dispatcher`. Чому жоден кур'єр не дістанеться двом замовленням? (`SREM` повертає 1 або 0.)
3. **Падіння.** `docker compose kill dispatcher`, зроби кілька замовлень, подивись `XPENDING`/`XLEN`, підніми диспетчера. Що з замовленнями?
4. **Rate limit.** Яка в «фіксованого вікна» діра на межі хвилини? Реалізуй ковзне вікно на ZSET.
5. **Нова фіча.** Додай ZSET заробітку кур'єрів (`lb:couriers:earnings`) і виведи його на дашборд.
6. **Продуктивність.** Порівняй `GET /restaurants/1/menu` з кешем і без нього через `ab`/`wrk`.
7. **Питання на розмову.** Що буде зі станом доставок, якщо перезапустити Redis без `appendonly`? Що збережеться в PostgreSQL?

## Локально без Docker (для відладки)

```bash
pip install -r requirements.txt
# потрібні запущені Redis і PostgreSQL (див. REDIS_URL, PG_DSN у app/config.py)
python -m app.dispatcher &  python -m app.simulator &  python -m app.generator &
uvicorn app.api:app --port 8100 &  python -m app.dashboard
```
