from datetime import date, datetime
from unittest.mock import MagicMock

import pytest
from freezegun import freeze_time

from wordgame_bot.league import League, NewEntry


def mock_cursor(league: League) -> MagicMock:
    return league.db.get_cursor.return_value.__enter__.return_value


def test_get_today_scores():
    league = League(MagicMock())
    mocked_cursor = mock_cursor(league)
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
        (date(2022, 3, 9), date(2022, 3, 7)),
        (date(2022, 3, 13), date(2022, 3, 7)),
        (date(2022, 3, 21), date(2022, 3, 21)),
        (date(2022, 1, 1), date(2021, 12, 27)),
    ],
)
def test_league_start_day(todays_date: date, expected_start: date):
    league = League(MagicMock())
    with freeze_time(todays_date):
        assert league.start_day == expected_start


def test_get_league_scores():
    league = League(MagicMock())
    mocked_cursor = mock_cursor(league)
    fetchall: MagicMock = mocked_cursor.fetchall
    fetchall.return_value = [
        ("tom", date(2022, 3, 11), 5),
        ("paul", date(2022, 3, 11), 51),
        ("tom", date(2022, 3, 9), 18),
        ("paul", date(2022, 3, 9), 16),
        ("jenny", date(2022, 3, 7), 6),
        ("tom", date(2022, 3, 7), 1),
        ("susan", date(2022, 3, 8), 23),
    ]
    league.get_league_scores()
    assert league.table == {
        "tom": {
            date(2022, 3, 9): 18,
            date(2022, 3, 11): 5,
            date(2022, 3, 7): 1,
        },
        "paul": {
            date(2022, 3, 9): 16,
            date(2022, 3, 11): 51,
        },
        "jenny": {date(2022, 3, 7): 6},
        "susan": {date(2022, 3, 8): 23},
    }


def test_get_league_table():
    league = League(MagicMock())
    mocked_cursor = mock_cursor(league)
    fetchall: MagicMock = mocked_cursor.fetchall
    fetchall.return_value = [
        ("tom", date(2022, 3, 11), 5),
        ("paul", date(2022, 3, 11), 51),
        ("tom", date(2022, 3, 9), 18),
        ("paul", date(2022, 3, 9), 16),
        ("jenny", date(2022, 3, 7), 6),
        ("tom", date(2022, 3, 7), 1),
        ("susan", date(2022, 3, 8), 23),
    ]
    league.get_league_scores()
    assert league.table == {
        "tom": {
            date(2022, 3, 9): 18,
            date(2022, 3, 11): 5,
            date(2022, 3, 7): 1,
        },
        "paul": {
            date(2022, 3, 9): 16,
            date(2022, 3, 11): 51,
        },
        "jenny": {date(2022, 3, 7): 6},
        "susan": {date(2022, 3, 8): 23},
    }


def test_get_latest_league_ranks():
    league = League(MagicMock())
    league.table = {
        "tom": {
            date(2022, 3, 9): 18,
            date(2022, 3, 11): 5,
            date(2022, 3, 7): 1,
        },
        "paul": {
            date(2022, 3, 9): 16,
            date(2022, 3, 11): 51,
        },
        "jenny": {date(2022, 3, 7): 6},
        "susan": {date(2022, 3, 8): 23},
    }
    ranks = league.get_latest_league_ranks()
    assert ranks == {
        "paul": (1, 67),
        "tom": (2, 24),
        "susan": (3, 23),
        "jenny": (4, 6),
    }


@freeze_time(datetime(2022, 3, 11))
def test_get_previous_league_ranks():
    league = League(MagicMock())
    league.table = {
        "tom": {
            date(2022, 3, 9): 18,
            date(2022, 3, 11): 5,
            date(2022, 3, 7): 1,
        },
        "paul": {
            date(2022, 3, 9): 16,
            date(2022, 3, 11): 51,
        },
        "jenny": {date(2022, 3, 7): 6},
        "susan": {date(2022, 3, 8): 23},
    }
    ranks = league.get_previous_league_ranks()
    assert ranks == {
        "susan": 1,
        "tom": 2,
        "paul": 3,
        "jenny": 4,
    }


@freeze_time(datetime(2022, 3, 11))
def test_get_previous_league_ranks_only_today():
    league = League(MagicMock())
    league.table = {
        "tom": {
            date(2022, 3, 11): 5,
        },
        "paul": {
            date(2022, 3, 11): 51,
        },
        "jenny": {date(2022, 3, 11): 6},
        "susan": {date(2022, 3, 11): 23},
    }
    ranks = league.get_previous_league_ranks()
    assert ranks == {}


@freeze_time(datetime(2022, 3, 11))
def test_get_league_info():
    league = League(MagicMock())
    league.table = {
        "tom": {
            date(2022, 3, 9): 18,
            date(2022, 3, 11): 5,
            date(2022, 3, 7): 1,
        },
        "paul": {
            date(2022, 3, 9): 16,
            date(2022, 3, 11): 51,
        },
        "jenny": {date(2022, 3, 7): 6},
        "susan": {date(2022, 3, 8): 23},
    }
    info = league.get_league_info()
    assert info == {
        "paul": (1, 2, 67),
        "tom": (2, 0, 24),
        "susan": (3, -2, 23),
        "jenny": (4, 0, 6),
    }


@freeze_time(datetime(2022, 3, 11))
def test_get_league_info_with_new_entry():
    league = League(MagicMock())
    league.table = {
        "tom": {
            date(2022, 3, 9): 18,
            date(2022, 3, 11): 5,
            date(2022, 3, 7): 1,
        },
        "paul": {
            date(2022, 3, 9): 16,
            date(2022, 3, 11): 51,
        },
        "jenny": {date(2022, 3, 7): 6},
        "susan": {date(2022, 3, 8): 23},
        "graham": {date(2022, 3, 11): 31},
    }
    info = league.get_league_info()
    expected = {
        "paul": (1, 2, 67),
        "graham": (2, NewEntry(), 31),
        "tom": (3, -1, 24),
        "susan": (4, -3, 23),
        "jenny": (5, -1, 6),
    }
    for user in expected:
        assert user in expected
        assert expected[user][0] == info[user][0]
        if isinstance(expected[user][1], NewEntry):
            assert isinstance(info[user][1], NewEntry)
        else:
            assert expected[user][1] == info[user][1]
        assert expected[user][2] == info[user][2]


def test_get_ranks_table():
    league = League(MagicMock())
    ranks = {
        "paul": (1, 2, 67),
        "graham": (2, NewEntry(), 31),
        "tom": (3, -1, 24),
        "susan": (4, -3, 23),
        "jenny": (5, -1, 6),
    }
    table = league.get_ranks_table(ranks)
    assert table == (
        "🔼 🥇. paul -- 67\n"
        "🟢 🥈. graham -- 31\n"
        "🔽 🥉. tom -- 24\n"
        "⏬  4. susan -- 23\n"
        "🔽  5. jenny -- 6"
    )


@freeze_time(datetime(2022, 3, 11))
def test_get_league():
    league = League(MagicMock())
    mocked_cursor = mock_cursor(league)
    fetchall: MagicMock = mocked_cursor.fetchall
    fetchall.return_value = [
        ("tom", date(2022, 3, 11), 5),
        ("graham", date(2022, 3, 11), 31),
        ("paul", date(2022, 3, 11), 51),
        ("tom", date(2022, 3, 9), 18),
        ("paul", date(2022, 3, 9), 16),
        ("jenny", date(2022, 3, 7), 6),
        ("tom", date(2022, 3, 7), 1),
        ("susan", date(2022, 3, 8), 23),
        ("lorraine", date(2022, 3, 8), 2),
        ("lorraine", date(2022, 3, 11), 65),
        ("simon", date(2022, 3, 10), 45),
        ("simon", date(2022, 3, 11), 27),
    ]
    table = league.get_league_table()
    league_contents = table.to_dict()
    fields = league_contents.get("fields", [])
    assert len(fields) == 1
    assert fields[0] == {
        "inline": False,
        "name": "=-------------------------------------------=",
        "value": (
            "▶️ 🥇. simon -- 72\n"
            "🔼 🥈. paul -- 67\n"
            "⏫ 🥉. lorraine -- 67\n"
            "🟢  4. graham -- 31\n"
            "⏬  5. tom -- 24\n"
            "⏬  6. susan -- 23\n"
            "⏬  7. jenny -- 6"
        ),
    }
    assert league_contents.get("title", "") == "🏆🏆🏆 League 🏆🏆🏆"
