"""Диспетчер: читає Stream, шукає НАЙБЛИЖЧОГО вільного кур'єра (GEO) і призначає його.

Запусти двох диспетчерів одночасно (DISPATCHER_NAME=d1 / d2) — consumer group розділить
замовлення між ними, а `SREM couriers:free` не дозволить віддати одного кур'єра двом замовленням.
"""
import os
import time

import redis

from . import config as C
from .config import get_redis
from .orders import publish_event
from .seed import seed_redis


def try_assign(r: redis.Redis, order_id) -> bool:
    order = r.hgetall(C.order_key(order_id))
    if not order or order.get("status") not in ("new", "waiting"):
        return True                                       # вже оброблено — нічого робити

    rest = r.hgetall(C.restaurant_key(order["restaurant_id"]))
    candidates = r.geosearch(C.COURIERS_GEO, longitude=float(rest["lon"]), latitude=float(rest["lat"]),
                             radius=C.DISPATCH_RADIUS_KM, unit="km", sort="ASC", count=20)
    for cid in candidates:                                # від найближчого до дальшого
        if r.srem(C.COURIERS_FREE, cid) == 1:             # атомарний «захват»: 1 — наш, 0 — вже зайнятий
            pipe = r.pipeline()
            pipe.hset(C.courier_key(cid), mapping={
                "status": "busy", "order_id": order_id, "phase": "to_restaurant",
                "target_lat": rest["lat"], "target_lon": rest["lon"]})
            pipe.hset(C.order_key(order_id), mapping={"status": "assigned", "courier_id": cid})
            pipe.zrem(C.ORDERS_WAITING, str(order_id))
            pipe.execute()
            name = r.hget(C.courier_key(cid), "name")
            publish_event(r, order_id, "assigned", f"#{order_id}: кур'єр {name} їде до «{rest['name']}»",
                          courier_id=cid)
            return True

    r.hset(C.order_key(order_id), "status", "waiting")
    r.zadd(C.ORDERS_WAITING, {str(order_id): time.time() + C.RETRY_WAITING_SEC})
    publish_event(r, order_id, "waiting", f"#{order_id}: вільних кур'єрів немає, чекаємо…")
    return False


def process_waiting(r: redis.Redis) -> None:
    for oid in r.zrangebyscore(C.ORDERS_WAITING, 0, time.time()):
        if r.zrem(C.ORDERS_WAITING, oid) == 1:            # лише один диспетчер забирає запис
            try_assign(r, oid)


def run() -> None:
    r = get_redis()
    seed_redis(r)
    me = os.getenv("DISPATCHER_NAME", "dispatcher-1")
    print(f"[{me}] запущено, чекаю замовлень…", flush=True)

    last_id = "0"        # спершу — НЕПІДТВЕРДЖЕНІ (pending) повідомлення, що лишились після падіння
    while True:
        resp = r.xreadgroup(C.ORDERS_GROUP, me, {C.ORDERS_STREAM: last_id}, count=10, block=1000)
        entries = resp[0][1] if resp else []
        if last_id == "0" and not entries:
            last_id = ">"                                 # pending закінчились → нові повідомлення
        for msg_id, fields in entries:
            try_assign(r, fields["order_id"])
            r.xack(C.ORDERS_STREAM, C.ORDERS_GROUP, msg_id)   # підтверджуємо ПІСЛЯ обробки
        process_waiting(r)


if __name__ == "__main__":
    run()
