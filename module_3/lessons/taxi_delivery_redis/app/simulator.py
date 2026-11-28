"""Симулятор кур'єрів: кожну секунду кожен зайнятий кур'єр робить крок до цілі.

   to_restaurant ──(дійшов)──▶ to_customer ──(дійшов)──▶ delivered
"""
import math
import time

import redis

from . import config as C
from . import db
from .config import get_redis
from .log import log
from .orders import publish_event
from .seed import seed_redis


def step_towards(lat, lon, tlat, tlon, step):
    """Один крок до цілі. Повертає (нова_широта, нова_довгота, чи_дійшов)."""
    dlat, dlon = tlat - lat, (tlon - lon) * math.cos(math.radians(lat))
    dist = math.hypot(dlat, dlon)
    if dist <= step:
        return tlat, tlon, True
    k = step / dist
    return lat + (tlat - lat) * k, lon + (tlon - lon) * k, False


def deliver(r: redis.Redis, cid: str, order_id: str) -> None:
    order = r.hgetall(C.order_key(order_id))
    now = time.time()
    order["delivered_at"] = now
    pipe = r.pipeline(transaction=True)
    pipe.hset(C.order_key(order_id), mapping={"status": "delivered", "delivered_at": now})
    pipe.expire(C.order_key(order_id), 3600)               # картка замовлення у Redis зникне за годину
    pipe.zrem(C.ORDERS_ACTIVE, order_id)
    pipe.zincrby(C.LB_COURIERS, 1, cid)                    # рейтинг кур'єрів
    pipe.zincrby(C.LB_RESTAURANTS, float(order["total"]), order["restaurant_id"])
    pipe.incr(C.STAT_DELIVERED)
    pipe.hset(C.courier_key(cid), mapping={"status": "free", "order_id": "", "phase": ""})
    pipe.sadd(C.COURIERS_FREE, cid)                        # кур'єр знову вільний
    res = pipe.execute()
    log.task("#%s доставлено кур'єром %s · %.0f грн", order_id, cid, float(order["total"]))
    log.redis("MULTI: HSET %s status=delivered, EXPIRE 3600, ZREM %s, ZINCRBY %s %s → %s, "
              "INCR %s → %s, SADD %s %s · EXEC", C.order_key(order_id), C.ORDERS_ACTIVE,
              C.LB_COURIERS, cid, int(res[3]), C.STAT_DELIVERED, res[5], C.COURIERS_FREE, cid)
    try:
        db.save_delivered_order(order)                     # «назавжди» — у PostgreSQL
    except Exception as exc:                               # Redis уже оновлено; у реальності — ретрай/черга
        log.warn("не вдалося записати #%s у PostgreSQL: %s", order_id, exc)
    publish_event(r, order_id, "delivered", f"#{order_id}: доставлено! 🎉 ({float(order['total']):.0f} грн)",
                  courier_id=cid)


def tick(r: redis.Redis) -> None:
    for cid in r.smembers(C.COURIERS_ALL):
        c = r.hgetall(C.courier_key(cid))
        if c.get("status") != "busy":
            continue
        pos = r.geopos(C.COURIERS_GEO, cid)[0]
        if pos is None:
            continue
        lon, lat = pos
        lat, lon, arrived = step_towards(lat, lon, float(c["target_lat"]), float(c["target_lon"]),
                                         C.COURIER_STEP_DEG)
        r.geoadd(C.COURIERS_GEO, (lon, lat, cid))          # оновили живу позицію
        log.debug("REDIS", "GEOADD %s %.5f %.5f %s (крок до цілі, фаза %s)", C.COURIERS_GEO, lon, lat, cid, c["phase"])
        if not arrived:
            continue

        order_id = c["order_id"]
        if c["phase"] == "to_restaurant":
            order = r.hgetall(C.order_key(order_id))
            r.hset(C.courier_key(cid), mapping={
                "phase": "to_customer", "target_lat": order["lat"], "target_lon": order["lon"]})
            r.hset(C.order_key(order_id), "status", "picked_up")
            log.task("#%s: кур'єр %s у ресторані, забрав їжу → їде до клієнта", order_id, cid)
            publish_event(r, order_id, "picked_up", f"#{order_id}: кур'єр забрав їжу, їде до клієнта",
                          courier_id=cid)
        else:
            deliver(r, cid, order_id)


def run() -> None:
    r = get_redis()
    seed_redis(r)
    log.task("кур'єри вийшли на маршрут: %d усього, %d вільних (крок кожну секунду)",
             r.scard(C.COURIERS_ALL), r.scard(C.COURIERS_FREE))
    while True:
        tick(r)
        time.sleep(1)


if __name__ == "__main__":
    run()
