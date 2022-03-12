import pytest
from unittest.mock import MagicMock, create_autospec, patch

from psycopg2._psycopg import connection

from wordgame_bot.db import DBConnection, NotConnected


@patch("wordgame_bot.db.connect")
def test_successful_connect_to_db(connect: MagicMock):
    mock_conn = MagicMock()
    connect.return_value = mock_conn
    db = DBConnection()
    with db.connect() as conn:
        connect.assert_called_once()
        assert conn == mock_conn
        assert db.conn == mock_conn
        mock_conn.close.assert_not_called()

    mock_conn.close.assert_called_once()


@patch("wordgame_bot.db.connect")
def test_get_cursor(connect: MagicMock):
    mock_conn = create_autospec(connection)
    connect.return_value = mock_conn
    db = DBConnection()
    with db.connect() as conn:
        with db.get_cursor() as _:
            conn.cursor.assert_called_once()


def test_get_cursor_not_connected():
    db = DBConnection()
    with pytest.raises(NotConnected):
        with db.get_cursor() as _:
            pass
