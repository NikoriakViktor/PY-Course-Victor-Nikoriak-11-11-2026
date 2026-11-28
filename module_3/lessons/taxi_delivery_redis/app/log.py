"""Логи проєкту: однаковий формат у всіх сервісах, щоб на занятті було видно шлях кожного замовлення.

Рядок починається з часу і тегу — ЩО саме сталося:

    TASK    крок бізнес-процесу: замовлення створено, кур'єра призначено, доставлено
    QUEUE   черга: Redis Stream (XADD / XREADGROUP / XACK) і відкладені повтори (ZSET orders:waiting)
    REDIS   інші команди Redis і їхній результат: кеш, лічильники, GEO, SET, HASH
    PG      PostgreSQL — «джерело правди»: що читаємо й записуємо
    EVENT   подія для дашборду й клієнтів (PUBLISH + LPUSH)
    WARN    щось пішло не так, але сервіс працює далі

Ім'я сервісу (api, dispatcher, simulator…) `docker compose logs` сам друкує зліва.
LOG_LEVEL=DEBUG покаже ще й дрібниці: кожен крок кур'єра, кожне пусте опитування черги.

    from .log import log
    log.queue("XADD %s → %s", key, msg_id)
"""
import logging
import os
import sys


class _Log:
    def __init__(self) -> None:
        self._log = logging.getLogger("taxi")
        if not self._log.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter("%(asctime)s  %(tag)-5s  %(message)s", datefmt="%H:%M:%S"))
            self._log.addHandler(handler)
            self._log.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
            self._log.propagate = False

    def _emit(self, level: int, tag: str, msg: str, *args) -> None:
        self._log.log(level, msg, *args, extra={"tag": tag})

    def task(self, msg, *a):  self._emit(logging.INFO, "TASK", msg, *a)
    def queue(self, msg, *a): self._emit(logging.INFO, "QUEUE", msg, *a)
    def redis(self, msg, *a): self._emit(logging.INFO, "REDIS", msg, *a)
    def pg(self, msg, *a):    self._emit(logging.INFO, "PG", msg, *a)
    def event(self, msg, *a): self._emit(logging.INFO, "EVENT", msg, *a)
    def warn(self, msg, *a):  self._emit(logging.WARNING, "WARN", msg, *a)
    def info(self, msg, *a):  self._emit(logging.INFO, "INFO", msg, *a)

    def debug(self, tag: str, msg, *a):
        self._emit(logging.DEBUG, tag, msg, *a)


log = _Log()
