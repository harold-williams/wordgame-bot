from contextlib import contextmanager
import os
from typing import Generator
from psycopg2 import connect
from psycopg2._psycopg import connection, cursor

DATABASE_URL = os.getenv("DATABASE_URL")


class DBConnection:
    url: str = DATABASE_URL

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
        with self.conn.cursor() as cursor:
            yield cursor
