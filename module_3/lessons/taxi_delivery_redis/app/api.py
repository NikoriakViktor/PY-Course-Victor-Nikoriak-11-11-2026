"""FastAPI — «вітрина» сервісу для клієнтів. Swagger: http://localhost:8100/docs"""
import json
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from . import config as C
from . import db
from .config import get_redis
from .menu import get_menu, invalidate_menu
from .orders import check_rate_limit, create_order
from .seed import seed_redis

r = get_redis()


@asynccontextmanager
async def lifespan(_: FastAPI):
    seed_redis(r)
    yield


app = FastAPI(title="Смачно + Таксі · Redis", lifespan=lifespan)


class Item(BaseModel):
    item_id: int
    qty: int = Field(1, ge=1, le=10)


class OrderIn(BaseModel):
    customer: str = Field(examples=["client-1"])
    restaurant_id: int
    items: list[Item] = Field(min_length=1)
    lat: float = C.CITY_LAT
    lon: float = C.CITY_LON


@app.get("/restaurants", summary="Ресторани поруч (Redis GEO)")
def restaurants(lat: float = C.CITY_LAT, lon: float = C.CITY_LON, radius_km: float = 5):
    found = r.geosearch(C.RESTAURANTS_GEO, longitude=lon, latitude=lat, radius=radius_km,
                        unit="km", sort="ASC", withdist=True)
    return [{"id": int(rid), "distance_km": round(dist, 2),
             **{k: r.hget(C.restaurant_key(rid), k) for k in ("name", "cuisine", "district")}}
            for rid, dist in found]


@app.get("/restaurants/{rid}/menu", summary="Меню (cache-aside: Redis → PostgreSQL)")
def menu(rid: int):
    items, source, ms = get_menu(r, rid)
    if not items:
        raise HTTPException(404, "Ресторан не знайдено")
    return {"source": source, "ms": round(ms, 2), "ttl_sec": r.ttl(C.menu_cache_key(rid)), "items": items}


@app.delete("/restaurants/{rid}/menu/cache", summary="Скинути кеш меню (інвалідація)")
def drop_menu_cache(rid: int):
    invalidate_menu(r, rid)
    return {"ok": True}


@app.post("/orders", status_code=201, summary="Зробити замовлення")
def make_order(body: OrderIn):
    if not check_rate_limit(r, body.customer):
        raise HTTPException(429, f"Не більше {C.ORDERS_PER_MIN_LIMIT} замовлень на хвилину")
    try:
        return create_order(r, body.customer, body.restaurant_id,
                            [i.model_dump() for i in body.items], body.lat, body.lon)
    except ValueError as e:
        raise HTTPException(422, str(e))


@app.get("/orders/{oid}", summary="Статус замовлення")
def order(oid: int):
    data = r.hgetall(C.order_key(oid))
    if not data:
        raise HTTPException(404, "Замовлення немає в Redis (завершені — у PostgreSQL: /history)")
    data["items"] = json.loads(data["items"])
    return data


@app.get("/couriers", summary="Кур'єри та їхні позиції (GEOPOS)")
def couriers():
    out = []
    for cid in sorted(r.smembers(C.COURIERS_ALL)):
        c = r.hgetall(C.courier_key(cid))
        pos = r.geopos(C.COURIERS_GEO, cid)[0]
        out.append({"id": cid, "name": c.get("name"), "status": c.get("status"),
                    "order_id": c.get("order_id") or None,
                    "lat": pos[1] if pos else None, "lon": pos[0] if pos else None})
    return out


@app.get("/leaderboard", summary="Рейтинг кур'єрів і ресторанів (Sorted Set)")
def leaderboard():
    top = r.zrevrange(C.LB_COURIERS, 0, 4, withscores=True)
    rest = r.zrevrange(C.LB_RESTAURANTS, 0, 4, withscores=True)
    return {
        "couriers": [{"id": cid, "name": r.hget(C.courier_key(cid), "name"), "deliveries": int(s)}
                     for cid, s in top],
        "restaurants": [{"id": int(rid), "name": r.hget(C.restaurant_key(rid), "name"), "revenue": s}
                        for rid, s in rest],
    }


@app.get("/stats", summary="Лічильники (INCR, HyperLogLog)")
def stats():
    hit, miss = int(r.get(C.STAT_CACHE_HIT) or 0), int(r.get(C.STAT_CACHE_MISS) or 0)
    return {
        "orders_today": int(r.get(f"stats:orders:{time.strftime('%Y-%m-%d')}") or 0),
        "delivered": int(r.get(C.STAT_DELIVERED) or 0),
        "active_orders": r.zcard(C.ORDERS_ACTIVE),
        "waiting_for_courier": r.zcard(C.ORDERS_WAITING),
        "free_couriers": r.scard(C.COURIERS_FREE),
        "unique_customers": r.pfcount(C.CUSTOMERS_UNIQUE),
        "stream_length": r.xlen(C.ORDERS_STREAM),
        "cache_hit_ratio": round(hit / (hit + miss), 2) if hit + miss else None,
    }


@app.get("/history", summary="Завершені замовлення з PostgreSQL")
def history(limit: int = 20):
    rows = db.history(limit)
    for row in rows:
        row["total"] = float(row["total"])
        row["delivered_at"] = row["delivered_at"].isoformat()
    return rows


@app.get("/events", summary="Live-події (Server-Sent Events поверх Redis Pub/Sub)")
def events():
    def stream():
        ps = get_redis().pubsub()                  # окреме з'єднання: підписник «зайнятий» слуханням
        ps.subscribe(C.EVENTS_CHANNEL)
        try:
            while True:
                msg = ps.get_message(ignore_subscribe_messages=True, timeout=15)
                yield f"data: {msg['data']}\n\n" if msg else ": keep-alive\n\n"
        finally:
            ps.close()
    return StreamingResponse(stream(), media_type="text/event-stream")
