"""Кеш меню: cache-aside (розділ 9 уроку 31).

  GET cache:menu:<id> ── є (hit)  ──▶ віддати з Redis
          └── нема (miss) ──▶ SELECT у PostgreSQL ──▶ SET ... EX 60 ──▶ віддати
"""
import json
import time

import redis

from . import config as C
from . import db


def get_menu(r: redis.Redis, restaurant_id: int) -> tuple[list[dict], str, float]:
    """Повертає (меню, звідки: 'cache' | 'db', мс)."""
    t0 = time.perf_counter()
    key = C.menu_cache_key(restaurant_id)

    cached = r.get(key)
    if cached is not None:
        r.incr(C.STAT_CACHE_HIT)
        return json.loads(cached), "cache", (time.perf_counter() - t0) * 1000

    menu = db.fetch_menu(restaurant_id)                       # повільний шлях — PostgreSQL
    r.set(key, json.dumps(menu, ensure_ascii=False), ex=C.MENU_TTL_SEC)
    r.incr(C.STAT_CACHE_MISS)
    return menu, "db", (time.perf_counter() - t0) * 1000


def invalidate_menu(r: redis.Redis, restaurant_id: int) -> None:
    """Змінили ціни в PostgreSQL → викинули кеш, щоб не віддавати застаріле."""
    r.delete(C.menu_cache_key(restaurant_id))
