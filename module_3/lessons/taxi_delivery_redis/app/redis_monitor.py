"""Redis MONITOR: кожна команда, яку отримує Redis, — з іменем сервісу, що її надіслав.

    docker compose logs -f redis-monitor

Ім'я сервісу береться з CLIENT SETNAME (див. get_redis у config.py): замість «172.18.0.5:40312»
видно «dispatcher». Команди, що повторюються щосекунди (дашборд, крок кур'єра, опитування черги),
за замовчуванням сховані, щоб було видно саму роботу. MONITOR_ALL=1 — показати геть усе.

MONITOR сповільнює Redis (кожна команда ще й пересилається сюди) — це інструмент для навчання
і відладки, а не для бойового сервера.
"""
import os
import re
import time

import redis

from . import config as C
from .log import log

SHOW_ALL = os.getenv("MONITOR_ALL", "0") == "1"
MAX_LEN = 180

# Шум, що повторюється щосекунди: (сервіс або *, перші слова команди)
NOISE = [
    ("dashboard", ""),                            # дашборд читає все раз на секунду
    ("simulator", "SMEMBERS couriers:all"), ("simulator", "HGETALL courier:"),
    ("simulator", "GEOPOS"), ("simulator", "GEOADD couriers:geo"),
    ("*", "XREADGROUP"), ("*", "ZRANGEBYSCORE orders:waiting"),
    ("*", "PING"), ("*", "CLIENT"), ("*", "HELLO"),
]


_HEX = re.compile(r"(?:\\x[0-9a-fA-F]{2})+")


def readable(text: str) -> str:
    """MONITOR екранує не-ASCII байти (\\xd0\\x9f…) — повертаємо кирилицю."""
    return _HEX.sub(lambda m: bytes.fromhex(m.group(0).replace("\\x", "")).decode("utf-8", "replace"), text)


def is_noise(service: str, command: str) -> bool:
    return any((s == "*" or s == service) and command.upper().startswith(p.upper()) for s, p in NOISE)


def run() -> None:
    r = redis.Redis.from_url(C.REDIS_URL, decode_responses=True, client_name="redis-monitor")
    while True:
        try:
            r.ping()
            break
        except redis.ConnectionError:
            time.sleep(1)
    names: dict[str, str] = {}

    def who(addr: str) -> str:
        if not names.get(addr):                    # нове з'єднання або ім'я ще не встигло з'явитись
            names.update({c["addr"]: c.get("name", "") for c in r.client_list()})
        return names.get(addr) or addr

    log.task("слухаю Redis (MONITOR). Режим: %s", "усі команди" if SHOW_ALL else
             "без щосекундних опитувань (MONITOR_ALL=1 — показати все)")
    with redis.Redis.from_url(C.REDIS_URL, decode_responses=True, client_name="redis-monitor").monitor() as m:
        for cmd in m.listen():
            service = who(f"{cmd.get('client_address')}:{cmd.get('client_port')}")
            text = readable(cmd.get("command", ""))
            if service == "redis-monitor" or (not SHOW_ALL and is_noise(service, text)):
                continue
            if len(text) > MAX_LEN:
                text = text[:MAX_LEN] + " …"
            print(f"{time.strftime('%H:%M:%S')}  {service:<11} ▶ {text}", flush=True)


if __name__ == "__main__":
    run()
