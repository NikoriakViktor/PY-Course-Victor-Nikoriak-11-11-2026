"""Генератор клієнтів: кожні кілька секунд хтось замовляє їжу. Щоб дашборд «жив»."""
import os
import random
import time

from . import config as C
from . import db
from .config import get_redis
from .log import log
from .menu import get_menu
from .orders import check_rate_limit, create_order
from .seed import seed_redis


def run() -> None:
    r = get_redis()
    seed_redis(r)
    restaurants = [x["id"] for x in db.fetch_restaurants()]
    pause = float(os.getenv("ORDER_EVERY_SEC", "6"))
    log.task("клієнти замовлятимуть приблизно кожні %.0f с (ORDER_EVERY_SEC)", pause)
    while True:
        customer = f"client-{random.randint(1, 25)}"
        rid = random.choice(restaurants)
        log.task("клієнт %s відкриває ресторан %s", customer, rid)
        if check_rate_limit(r, customer):
            menu, _, _ = get_menu(r, rid)
            items = [{"item_id": m["id"], "qty": random.randint(1, 2)}
                     for m in random.sample(menu, k=random.randint(1, 3))]
            create_order(r, customer, rid, items,
                         C.CITY_LAT + random.uniform(-0.04, 0.04),
                         C.CITY_LON + random.uniform(-0.08, 0.08))
        time.sleep(random.uniform(pause * 0.5, pause * 1.5))


if __name__ == "__main__":
    run()
