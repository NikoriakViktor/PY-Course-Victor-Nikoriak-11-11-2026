"""Диспетчер: читає Stream, шукає НАЙБЛИЖЧОГО вільного кур'єра (GEO) і призначає його.

Запусти двох диспетчерів одночасно (DISPATCHER_NAME=d1 / d2) — consumer group розділить
замовлення між ними, а `SREM couriers:free` не дозволить віддати одного кур'єра двом замовленням.

У логах видно весь шлях замовлення через чергу:
    QUEUE  XREADGROUP … → 1 повідомлення        (взяли з черги)
    REDIS  GEOSEARCH … → c4 0.8 км, c2 1.3 км    (хто найближче)
    REDIS  SREM couriers:free c4 → 1             (захопили кур'єра)
    QUEUE  XACK … → 1                            (підтвердили: повідомлення оброблено)
"""
import os
import time

import redis

from . import config as C
from .config import get_redis
from .log import log
from .orders import publish_event
from .seed import seed_redis


def try_assign(r: redis.Redis, order_id) -> bool:
    order = r.hgetall(C.order_key(order_id))
    if not order or order.get("status") not in ("new", "waiting"):
        log.task("#%s уже має статус «%s» — пропускаю", order_id, order.get("status", "немає в Redis"))
        return True                                       # вже оброблено — нічого робити

    rest = r.hgetall(C.restaurant_key(order["restaurant_id"]))
    candidates = r.geosearch(C.COURIERS_GEO, longitude=float(rest["lon"]), latitude=float(rest["lat"]),
                             radius=C.DISPATCH_RADIUS_KM, unit="km", sort="ASC", count=20, withdist=True)
    free = r.smembers(C.COURIERS_FREE)
    log.redis("GEOSEARCH %s біля «%s» → %s · вільні: %s", C.COURIERS_GEO, rest["name"],
              ", ".join(f"{cid} {dist:.1f} км" for cid, dist in candidates[:5]) or "нікого",
              ", ".join(sorted(free)) or "нікого")
    for cid, dist in candidates:                          # від найближчого до дальшого
        if r.srem(C.COURIERS_FREE, cid) == 1:             # атомарний «захват»: 1 — наш, 0 — вже зайнятий
            log.redis("SREM %s %s → 1 (кур'єр наш, ніхто інший його вже не візьме)", C.COURIERS_FREE, cid)
            pipe = r.pipeline()
            pipe.hset(C.courier_key(cid), mapping={
                "status": "busy", "order_id": order_id, "phase": "to_restaurant",
                "target_lat": rest["lat"], "target_lon": rest["lon"]})
            pipe.hset(C.order_key(order_id), mapping={"status": "assigned", "courier_id": cid})
            pipe.zrem(C.ORDERS_WAITING, str(order_id))
            pipe.execute()
            name = r.hget(C.courier_key(cid), "name")
            log.task("#%s → кур'єр %s (%s), %.1f км до ресторану", order_id, cid, name, dist)
            publish_event(r, order_id, "assigned", f"#{order_id}: кур'єр {name} їде до «{rest['name']}»",
                          courier_id=cid)
            return True
        if cid in free:                                   # був вільним, але його щойно взяв інший диспетчер
            log.redis("SREM %s %s → 0 (вже зайнятий іншим, пробую наступного)", C.COURIERS_FREE, cid)

    retry_at = time.time() + C.RETRY_WAITING_SEC
    r.hset(C.order_key(order_id), "status", "waiting")
    r.zadd(C.ORDERS_WAITING, {str(order_id): retry_at})
    log.queue("#%s: вільних кур'єрів немає → ZADD %s (повтор через %d с)",
              order_id, C.ORDERS_WAITING, C.RETRY_WAITING_SEC)
    publish_event(r, order_id, "waiting", f"#{order_id}: вільних кур'єрів немає, чекаємо…")
    return False


def process_waiting(r: redis.Redis) -> None:
    for oid in r.zrangebyscore(C.ORDERS_WAITING, 0, time.time()):
        if r.zrem(C.ORDERS_WAITING, oid) == 1:            # лише один диспетчер забирає запис
            log.queue("ZRANGEBYSCORE %s: настав час повтору → #%s, шукаю кур'єра знову", C.ORDERS_WAITING, oid)
            try_assign(r, oid)


def run() -> None:
    r = get_redis()
    seed_redis(r)
    me = os.getenv("DISPATCHER_NAME", "dispatcher-1")
    info = {g["name"]: g for g in r.xinfo_groups(C.ORDERS_STREAM)}.get(C.ORDERS_GROUP, {})
    log.task("%s запущено. Черга %s: довжина %d, група «%s», непідтверджених (pending) %s",
             me, C.ORDERS_STREAM, r.xlen(C.ORDERS_STREAM), C.ORDERS_GROUP, info.get("pending", 0))

    last_id = "0"        # спершу — НЕПІДТВЕРДЖЕНІ (pending) повідомлення, що лишились після падіння
    while True:
        resp = r.xreadgroup(C.ORDERS_GROUP, me, {C.ORDERS_STREAM: last_id}, count=10, block=1000)
        entries = resp[0][1] if resp else []
        if last_id == "0":
            if entries:
                log.queue("XREADGROUP %s %s ... 0 → %d НЕпідтверджених після падіння, доробляю",
                          C.ORDERS_GROUP, me, len(entries))
            else:
                log.queue("pending порожній → тепер читаю нові повідомлення (XREADGROUP ... >)")
                last_id = ">"                             # pending закінчились → нові повідомлення
        elif entries:
            log.queue("XREADGROUP %s %s ... > → нових повідомлень: %d — %s", C.ORDERS_GROUP, me, len(entries),
                      ", ".join(f"{mid} (#{f['order_id']})" for mid, f in entries))
        else:
            log.debug("QUEUE", "XREADGROUP: за 1 с нічого нового")
        for msg_id, fields in entries:
            try_assign(r, fields["order_id"])
            acked = r.xack(C.ORDERS_STREAM, C.ORDERS_GROUP, msg_id)   # підтверджуємо ПІСЛЯ обробки
            log.queue("XACK %s %s %s → %d (оброблено, з pending прибрано)", C.ORDERS_STREAM, C.ORDERS_GROUP,
                      msg_id, acked)
        process_waiting(r)


if __name__ == "__main__":
    run()
