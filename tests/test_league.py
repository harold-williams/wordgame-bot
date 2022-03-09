from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from freezegun import freeze_time

from wordgame_bot.league import League


def test_get_today_scores():
    league = League(MagicMock())
    mocked_cursor: MagicMock = league.conn.cursor.return_value.__enter__.return_value
    fetchall: MagicMock = mocked_cursor.fetchall
    fetchall.return_value = [
        ("tom", 5),
        ("paul", 18),
        ("jenny", 6),
        ("graham", 1),
        ("susan", 23),
    ]
    league.get_today_scores()
    assert league.scores == {
        "tom": 5,
        "paul": 18,
        "jenny": 6,
        "graham": 1,
        "susan": 23,
    }

@pytest.mark.parametrize(
    "todays_date, expected_start",
    [
        (datetime(2022, 3, 9), datetime(2022, 3, 7)),
        (datetime(2022, 3, 13), datetime(2022, 3, 7)),
        (datetime(2022, 3, 21), datetime(2022, 3, 21)),
        (datetime(2022, 1, 1), datetime(2021, 12, 27)),
    ]
)
def test_league_start_day(todays_date: datetime, expected_start: datetime):
    league = League(MagicMock())
    with freeze_time(todays_date):
        assert league.start_day == expected_start

def test_get_league_scores():
    league = League(MagicMock())
    mocked_cursor: MagicMock = league.conn.cursor.return_value.__enter__.return_value
    fetchall: MagicMock = mocked_cursor.fetchall
    fetchall.return_value = [
        ("tom", datetime(2022, 3, 11), 5),
        ("paul", datetime(2022, 3, 11), 51),
        ("tom", datetime(2022, 3, 9), 18),
        ("paul", datetime(2022, 3, 9), 16),
        ("jenny", datetime(2022, 3, 7), 6),
        ("tom", datetime(2022, 3, 7), 1),
        ("susan", datetime(2022, 3, 8), 23),
    ]
    league.get_league_scores()
    assert league.table == {
        "tom": {
            datetime(2022, 3, 9): 18,
            datetime(2022, 3, 11): 5,
            datetime(2022, 3, 7): 1,
        },
        "paul": {
            datetime(2022, 3, 9): 16,
            datetime(2022, 3, 11): 51,
        },
        "jenny": {datetime(2022, 3, 7): 6},
        "susan": {datetime(2022, 3, 8): 23},
    }

def test_get_league_table():
    league = League(MagicMock())
    mocked_cursor: MagicMock = league.conn.cursor.return_value.__enter__.return_value
    fetchall: MagicMock = mocked_cursor.fetchall
    fetchall.return_value = [
        ("tom", datetime(2022, 3, 11), 5),
        ("paul", datetime(2022, 3, 11), 51),
        ("tom", datetime(2022, 3, 9), 18),
        ("paul", datetime(2022, 3, 9), 16),
        ("jenny", datetime(2022, 3, 7), 6),
        ("tom", datetime(2022, 3, 7), 1),
        ("susan", datetime(2022, 3, 8), 23),
    ]
    league.get_league_scores()
    assert league.table == {
        "tom": {
            datetime(2022, 3, 9): 18,
            datetime(2022, 3, 11): 5,
            datetime(2022, 3, 7): 1,
        },
        "paul": {
            datetime(2022, 3, 9): 16,
            datetime(2022, 3, 11): 51,
        },
        "jenny": {datetime(2022, 3, 7): 6},
        "susan": {datetime(2022, 3, 8): 23},
    }

def test_get_latest_league_ranks():
    league = League(MagicMock())
    league.table = {
        "tom": {
            datetime(2022, 3, 9): 18,
            datetime(2022, 3, 11): 5,
            datetime(2022, 3, 7): 1,
        },
        "paul": {
            datetime(2022, 3, 9): 16,
            datetime(2022, 3, 11): 51,
        },
        "jenny": {datetime(2022, 3, 7): 6},
        "susan": {datetime(2022, 3, 8): 23},
    }
    ranks = league.get_latest_league_ranks()
    assert ranks == [
        (1, "paul", 67),
        (2, "tom", 24),
        (3, "susan", 23),
        (4, "jenny", 6),
    ]

@freeze_time(datetime(2022,3,11))
def test_get_previous_league_ranks():
    league = League(MagicMock())
    league.table = {
        "tom": {
            datetime(2022, 3, 9): 18,
            datetime(2022, 3, 11): 5,
            datetime(2022, 3, 7): 1,
        },
        "paul": {
            datetime(2022, 3, 9): 16,
            datetime(2022, 3, 11): 51,
        },
        "jenny": {datetime(2022, 3, 7): 6},
        "susan": {datetime(2022, 3, 8): 23},
    }
    ranks = league.get_previous_league_ranks()
    assert ranks == [
        (1, "susan", 23),
        (2, "tom", 19),
        (3, "paul", 16),
        (4, "jenny", 6),
    ]

@freeze_time(datetime(2022,3,11))
def test_get_previous_league_ranks():
    league = League(MagicMock())
    league.table = {
        "tom": {
            datetime(2022, 3, 11): 5,
        },
        "paul": {
            datetime(2022, 3, 11): 51,
        },
        "jenny": {datetime(2022, 3, 11): 6},
        "susan": {datetime(2022, 3, 11): 23},
    }
    ranks = league.get_previous_league_ranks()
    assert ranks == []

@freeze_time(datetime(2022,3,11))
def test_get_rank_difference():
    league = League(MagicMock())
    league.table = {
        "tom": {
            datetime(2022, 3, 9): 18,
            datetime(2022, 3, 11): 5,
            datetime(2022, 3, 7): 1,
        },
        "paul": {
            datetime(2022, 3, 9): 16,
            datetime(2022, 3, 11): 51,
        },
        "jenny": {datetime(2022, 3, 7): 6},
        "susan": {datetime(2022, 3, 8): 23},
    }
    differences = league.get_rank_difference()
    assert differences == [
        (2, "paul"),
        (0, "tom"),
        (-2, "susan"),
        (-1, "jenny"),
    ]