from __future__ import annotations

import os
from collections.abc import Generator
from contextlib import contextmanager

from psycopg2 import connect
from psycopg2._psycopg import connection, cursor

DATABASE_URL = os.getenv("DATABASE_URL")


class NotConnected(Exception):
    pass


class DBConnection:
    url: str = DATABASE_URL
    conn: connection | None = None

    @contextmanager
    def connect(self) -> Generator[connection, None, None]:
        try:
            self.conn = connect(self.url, sslmode="require")
            yield self.conn
        finally:
            self.conn.close()

    @contextmanager
    def commit(self) -> None:
        self.conn.commit()

    @contextmanager
    def rollback(self) -> None:
        self.conn.rollback()

    @contextmanager
    def get_cursor(self) -> Generator[cursor, None, None]:
        if self.conn is not None:
            with self.conn.cursor() as cursor:
                yield cursor
        else:
            raise NotConnected()
