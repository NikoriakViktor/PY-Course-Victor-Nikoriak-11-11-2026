"""Кеш меню: cache-aside (розділ 9 уроку 31).

  GET cache:menu:<id> ── є (hit)  ──▶ віддати з Redis
          └── нема (miss) ──▶ SELECT у PostgreSQL ──▶ SET ... EX 60 ──▶ віддати
"""
import json
import time

import redis

from . import config as C
from . import db
from .log import log


def get_menu(r: redis.Redis, restaurant_id: int) -> tuple[list[dict], str, float]:
    """Повертає (меню, звідки: 'cache' | 'db', мс)."""
    t0 = time.perf_counter()
    key = C.menu_cache_key(restaurant_id)

    cached = r.get(key)
    if cached is not None:
        r.incr(C.STAT_CACHE_HIT)
        ms = (time.perf_counter() - t0) * 1000
        log.redis("GET %s → HIT (кеш, %.1f мс, TTL ще %s с)", key, ms, r.ttl(key))
        return json.loads(cached), "cache", ms

    log.redis("GET %s → MISS (кешу немає) → іду в PostgreSQL", key)
    menu = db.fetch_menu(restaurant_id)                       # повільний шлях — PostgreSQL
    r.set(key, json.dumps(menu, ensure_ascii=False), ex=C.MENU_TTL_SEC)
    r.incr(C.STAT_CACHE_MISS)
    ms = (time.perf_counter() - t0) * 1000
    log.redis("SET %s EX %d → кеш на %d с (разом %.1f мс)", key, C.MENU_TTL_SEC, C.MENU_TTL_SEC, ms)
    return menu, "db", ms


def invalidate_menu(r: redis.Redis, restaurant_id: int) -> None:
    """Змінили ціни в PostgreSQL → викинули кеш, щоб не віддавати застаріле."""
    deleted = r.delete(C.menu_cache_key(restaurant_id))
    log.redis("DEL %s → %d (кеш скинуто, наступний запит піде в PostgreSQL)", C.menu_cache_key(restaurant_id), deleted)
