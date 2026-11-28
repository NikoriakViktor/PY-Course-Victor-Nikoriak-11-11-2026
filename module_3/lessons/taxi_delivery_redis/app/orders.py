"""Створення замовлення: усе, що відбувається, коли клієнт натиснув «Замовити»."""
import json
import time

import redis

from . import config as C
from .menu import get_menu


def check_rate_limit(r: redis.Redis, customer: str) -> bool:
    """Не більше N замовлень за хвилину з одного клієнта (фіксоване вікно: INCR + EXPIRE)."""
    key = C.ratelimit_key(customer)
    n = r.incr(key)
    if n == 1:
        r.expire(key, 60)
    return n <= C.ORDERS_PER_MIN_LIMIT


def publish_event(r: redis.Redis, order_id, status: str, text: str, **extra) -> None:
    """Подія йде двома шляхами:
       • PUBLISH — отримають лише ті, хто слухає ПРЯМО ЗАРАЗ (SSE, дашборд);
       • LPUSH + LTRIM — «стрічка», щоб нові відвідувачі побачили останні 30 подій."""
    event = json.dumps({"ts": time.time(), "order_id": int(order_id), "status": status,
                        "text": text, **extra}, ensure_ascii=False)
    pipe = r.pipeline()
    pipe.publish(C.EVENTS_CHANNEL, event)
    pipe.lpush(C.EVENTS_LOG, event)
    pipe.ltrim(C.EVENTS_LOG, 0, 29)
    pipe.execute()


def create_order(r: redis.Redis, customer: str, restaurant_id: int,
                 items: list[dict], lat: float, lon: float) -> dict:
    """items: [{"item_id": 7, "qty": 2}, ...]. Ціни беремо з меню (кеш → PostgreSQL), а не від клієнта."""
    if not r.exists(C.restaurant_key(restaurant_id)):
        raise ValueError(f"Ресторану {restaurant_id} не існує")

    menu, _, _ = get_menu(r, restaurant_id)
    prices = {m["id"]: m for m in menu}
    lines, total = [], 0.0
    for it in items:
        dish = prices.get(it["item_id"])
        if dish is None:
            raise ValueError(f"Страви {it['item_id']} немає в меню ресторану {restaurant_id}")
        qty = max(1, int(it.get("qty", 1)))
        lines.append({"item_id": dish["id"], "name": dish["name"], "qty": qty, "price": dish["price"]})
        total += dish["price"] * qty

    order_id = r.incr(C.ORDER_SEQ)                       # унікальний id без PostgreSQL
    now = time.time()
    pipe = r.pipeline(transaction=True)                  # MULTI/EXEC: або все, або нічого
    pipe.hset(C.order_key(order_id), mapping={
        "id": order_id, "customer": customer, "restaurant_id": restaurant_id,
        "items": json.dumps(lines, ensure_ascii=False), "total": round(total, 2),
        "lat": lat, "lon": lon, "status": "new", "courier_id": "", "created_at": now})
    pipe.xadd(C.ORDERS_STREAM, {"order_id": order_id})   # черга для диспетчерів
    pipe.zadd(C.ORDERS_ACTIVE, {str(order_id): now})     # «активні» для дашборду
    pipe.incr(f"stats:orders:{time.strftime('%Y-%m-%d')}")   # лічильник «замовлень за день»
    pipe.pfadd(C.CUSTOMERS_UNIQUE, customer)             # унікальні клієнти (HyperLogLog)
    pipe.execute()

    rest_name = r.hget(C.restaurant_key(restaurant_id), "name")
    publish_event(r, order_id, "new", f"Нове замовлення #{order_id} · {rest_name} · {total:.0f} грн")
    return {"order_id": order_id, "total": round(total, 2), "status": "new"}
