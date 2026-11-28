"""Прогрів Redis з PostgreSQL: GEO ресторанів і стартові позиції кур'єрів. Ідемпотентно."""
import random

import redis

from . import config as C
from . import db
from .log import log


def seed_redis(r: redis.Redis) -> None:
    db.wait_for_db()

    pipe = r.pipeline()
    for rest in db.fetch_restaurants():
        pipe.geoadd(C.RESTAURANTS_GEO, (rest["lon"], rest["lat"], str(rest["id"])))
        pipe.hset(C.restaurant_key(rest["id"]), mapping={
            "name": rest["name"], "cuisine": rest["cuisine"], "district": rest["district"],
            "lat": rest["lat"], "lon": rest["lon"]})
    pipe.execute()
    log.redis("GEOADD %s + HSET restaurant:* — ресторани з PostgreSQL прогріто в Redis", C.RESTAURANTS_GEO)

    rng = random.Random(42)
    for cour in db.fetch_couriers():
        cid = cour["id"]
        if r.sismember(C.COURIERS_ALL, cid):
            continue                                  # уже є — позицію не чіпаємо
        lat = C.CITY_LAT + rng.uniform(-0.04, 0.04)
        lon = C.CITY_LON + rng.uniform(-0.08, 0.08)
        pipe = r.pipeline()
        pipe.geoadd(C.COURIERS_GEO, (lon, lat, cid))
        pipe.hset(C.courier_key(cid), mapping={"name": cour["name"], "status": "free"})
        pipe.sadd(C.COURIERS_ALL, cid)
        pipe.sadd(C.COURIERS_FREE, cid)
        pipe.execute()

    try:  # Consumer group для Stream; MKSTREAM створює стрім, якщо його ще нема
        r.xgroup_create(C.ORDERS_STREAM, C.ORDERS_GROUP, id="0", mkstream=True)
        log.queue("XGROUP CREATE %s %s MKSTREAM → черга і група диспетчерів створені", C.ORDERS_STREAM, C.ORDERS_GROUP)
    except redis.ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise
