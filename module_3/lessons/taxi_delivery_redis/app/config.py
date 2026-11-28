"""Налаштування та ВСІ назви ключів Redis в одному місці.

Правило проєкту: назви ключів пишемо лише тут — так студенти бачать «карту» даних.
Формат ключів:  <сутність>:<id>  або  <група>:<призначення>.
"""
import os

import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
PG_DSN = os.getenv("PG_DSN", "postgresql://taxi:taxi@localhost:5434/smachno")

# центр Києва та параметри симуляції
CITY_LAT, CITY_LON = 50.4501, 30.5234
MENU_TTL_SEC = 60                                   # скільки живе кеш меню
COURIER_STEP_DEG = float(os.getenv("COURIER_STEP", "0.003"))   # крок кур'єра за тік (~330 м)
DELIVERY_FEE = 50                                   # грн кур'єру за доставку
ORDERS_PER_MIN_LIMIT = 3                            # rate limit на клієнта (як у уроці 31)
DISPATCH_RADIUS_KM = 15
RETRY_WAITING_SEC = 3                               # через скільки повторити пошук кур'єра

# ── ключі ───────────────────────────────────────────────────────────────────
RESTAURANTS_GEO = "restaurants:geo"        # GEO      — координати ресторанів
COURIERS_GEO = "couriers:geo"              # GEO      — живі координати кур'єрів
COURIERS_ALL = "couriers:all"              # SET      — усі кур'єри
COURIERS_FREE = "couriers:free"            # SET      — вільні кур'єри (SREM = атомарний «захват»)
ORDER_SEQ = "order:seq"                    # STRING   — лічильник id замовлень (INCR)
ORDERS_STREAM = "orders:new"               # STREAM   — черга нових замовлень
ORDERS_GROUP = "dispatchers"               # consumer group диспетчерів
ORDERS_ACTIVE = "orders:active"            # ZSET     — активні замовлення (score = час створення)
ORDERS_WAITING = "orders:waiting"          # ZSET     — немає кур'єра, повтор пізніше (score = коли)
EVENTS_CHANNEL = "events:orders"           # PUB/SUB  — live-події
EVENTS_LOG = "events:log"                  # LIST     — останні події (Pub/Sub нічого не зберігає!)
LB_COURIERS = "lb:couriers:deliveries"     # ZSET     — рейтинг кур'єрів за доставками
LB_RESTAURANTS = "lb:restaurants:revenue"  # ZSET     — виторг ресторанів
CUSTOMERS_UNIQUE = "stats:customers:unique"  # HyperLogLog — унікальні клієнти
STAT_DELIVERED = "stats:delivered"         # STRING (INCR)
STAT_CACHE_HIT = "stats:cache:hit"
STAT_CACHE_MISS = "stats:cache:miss"


def restaurant_key(rid) -> str: return f"restaurant:{rid}"        # HASH
def courier_key(cid) -> str: return f"courier:{cid}"              # HASH
def order_key(oid) -> str: return f"order:{oid}"                  # HASH
def menu_cache_key(rid) -> str: return f"cache:menu:{rid}"        # STRING + TTL
def ratelimit_key(customer: str) -> str: return f"ratelimit:{customer}"  # STRING + TTL


SERVICE = os.getenv("SERVICE", "local")     # ім'я сервісу з docker-compose.yml


def get_redis() -> redis.Redis:
    """decode_responses=True → працюємо зі str, а не з bytes.
    client_name → у `CLIENT LIST` і в redis-monitor видно, ЯКИЙ сервіс надіслав команду."""
    return redis.Redis.from_url(REDIS_URL, decode_responses=True, client_name=SERVICE)
