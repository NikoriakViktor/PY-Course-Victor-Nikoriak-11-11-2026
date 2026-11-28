"""PostgreSQL — джерело правди. Тут лише прості SQL-функції (урок 30).

Для навчання відкриваємо нове з'єднання на кожен виклик. У бойовому коді тут був би пул з'єднань.
"""
import json
import time

import psycopg
from psycopg.rows import dict_row

from . import config as C
from .log import log


def connect() -> psycopg.Connection:
    # application_name → у логах PostgreSQL видно, який сервіс виконав запит
    return psycopg.connect(C.PG_DSN, row_factory=dict_row, autocommit=True, application_name=C.SERVICE)


def wait_for_db(retries: int = 60) -> None:
    for attempt in range(1, retries + 1):
        try:
            connect().close()
            log.pg("підключився до PostgreSQL (спроба %d)", attempt)
            return
        except psycopg.OperationalError as exc:
            reason = str(exc).strip().splitlines()[0] if str(exc).strip() else type(exc).__name__
            log.warn("PostgreSQL ще недоступний (спроба %d/%d): %s", attempt, retries, reason)
            time.sleep(1)
    raise RuntimeError(
        "PostgreSQL недоступний. Перевір `docker compose ps` і `docker compose logs postgres`; "
        "якщо контейнер postgres без мережі чи порту — `docker compose down`, потім `docker compose up --build`.")


def fetch_restaurants() -> list[dict]:
    with connect() as con:
        return con.execute("SELECT * FROM restaurants ORDER BY id").fetchall()


def fetch_menu(restaurant_id: int) -> list[dict]:
    with connect() as con:
        rows = con.execute(
            "SELECT id, name, price FROM menu_items WHERE restaurant_id = %s ORDER BY id",
            (restaurant_id,),                       # параметри, а не f-рядок!
        ).fetchall()
    log.pg("SELECT menu_items WHERE restaurant_id=%s → страв у меню: %d", restaurant_id, len(rows))
    return [{"id": r["id"], "name": r["name"], "price": float(r["price"])} for r in rows]


def fetch_couriers() -> list[dict]:
    with connect() as con:
        return con.execute("SELECT id, name FROM couriers ORDER BY id").fetchall()


def save_delivered_order(o: dict) -> None:
    """Завершене замовлення — назавжди в PostgreSQL. Повторний виклик безпечний (ON CONFLICT)."""
    with connect() as con:
        con.execute(
            """
            INSERT INTO orders (id, customer, restaurant_id, courier_id, items, total, fee,
                                created_at, delivered_at, lat, lon)
            VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s,
                    to_timestamp(%s), to_timestamp(%s), %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (int(o["id"]), o["customer"], int(o["restaurant_id"]), o["courier_id"],
             o["items"] if isinstance(o["items"], str) else json.dumps(o["items"]),
             float(o["total"]), C.DELIVERY_FEE,
             float(o["created_at"]), float(o["delivered_at"]),
             float(o["lat"]), float(o["lon"])),
        )
    log.pg("INSERT INTO orders #%s (%s грн) — замовлення збережено назавжди", o["id"], o["total"])


def history(limit: int = 20) -> list[dict]:
    with connect() as con:
        return con.execute(
            "SELECT id, customer, restaurant_id, courier_id, total, delivered_at "
            "FROM orders ORDER BY id DESC LIMIT %s", (limit,)).fetchall()
