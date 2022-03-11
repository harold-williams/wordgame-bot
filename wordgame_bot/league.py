from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from discord import Color, Embed

from wordgame_bot.db import DBConnection

DATABASE_URL = os.getenv("DATABASE_URL")

SCORES = """
SELECT username, submission_date, total
FROM (
    SELECT
        user_id,
        submission_date,
        SUM (score) AS total
    FROM
        attempts AS a
    WHERE
        submission_date = %s
    GROUP BY
        user_id
    ORDER BY total DESC
) scores
INNER JOIN users
    ON scores.user_id = users.user_id;
"""

LEAGUE_TABLE = """
SELECT username, submission_date, total
FROM (
    SELECT
        user_id,
        submission_date,
        SUM (score) AS total
    FROM
        attempts AS a
    WHERE
        mode != 'O'
        AND submission_date IS NOT NULL
        AND submission_date >= %s
    GROUP BY
        user_id, submission_date
    ORDER BY total DESC
) scores
INNER JOIN users
    ON scores.user_id = users.user_id;
"""


class NewEntry:
    pass


@dataclass
class League:
    db: DBConnection
    League_length: timedelta = timedelta(days=7)
    scores: dict[int, int] = field(default_factory=dict)
    table: dict[str, dict[datetime, int]] = field(default_factory=dict)

    @property
    def start_day(self):
        today = date.today()
        return today - timedelta(days=today.weekday())

    def get_league_table(self):
        self.get_league_scores()
        info = self.get_league_info()
        return self.format_league(info)

    def get_today_scores(self):
        self.scores = {}
        with self.db.get_cursor() as curs:
            curs.execute(SCORES, (datetime.today(),))
            retrieved_scores = curs.fetchall()
            for (user_id, score) in retrieved_scores:
                self.scores[user_id] = score

    def get_league_scores(self):
        self.table = {}
        with self.db.get_cursor() as curs:
            curs.execute(LEAGUE_TABLE, (self.start_day,))
            retrieved_scores = curs.fetchall()
            for (user_id, day, score) in retrieved_scores:
                self.table.setdefault(user_id, {})[day] = score

    def get_latest_league_ranks(self):
        ranks = [
            (username, sum(scores.values()))
            for username, scores in self.table.items()
        ]
        ranks.sort(key=lambda x: x[1], reverse=True)
        return {
            user: (rank + 1, score)
            for rank, (user, score) in enumerate(ranks)
            if score != 0
        }

    def get_previous_league_ranks(self):
        ranks = [
            (
                username,
                sum(
                    score
                    for day, score in scores.items()
                    if day != date.today()
                ),
            )
            for username, scores in self.table.items()
        ]
        ranks.sort(key=lambda x: x[1], reverse=True)
        return {
            user: rank + 1
            for rank, (user, score) in enumerate(ranks)
            if score != 0
        }

    def get_league_info(self):
        previous_ranks = self.get_previous_league_ranks()
        current_ranks = self.get_latest_league_ranks()
        rank_info = {}
        for user, (rank, score) in current_ranks.items():
            if user in previous_ranks:
                rank_info[user] = (rank, previous_ranks[user] - rank, score)
            else:
                rank_info[user] = (rank, NewEntry(), score)
        return rank_info

    def get_ranks_table(self, ranks):
        rank_table = "\n".join(
            f"{self.get_diff_symbol(diff)} {self.get_rank_value(rank)}. {user} -- {score}"
            for user, (rank, diff, score) in ranks.items()
        )
        return rank_table

    @staticmethod
    def get_rank_value(rank):
        rank_strings = {1: "🥇", 2: "🥈", 3: "🥉"}
        return rank_strings.get(rank, f"{rank:>2}")

    @staticmethod
    def get_diff_symbol(diff):
        if isinstance(diff, NewEntry):
            return "🟢"
        elif diff > 2:
            return "⏫"
        elif diff > 0:
            return "🔼"
        elif diff == 0:
            return "▶️"
        elif diff > -2:
            return "🔽"
        return "⏬"

    def format_league(self, ranks) -> Embed:
        rank_table = self.get_ranks_table(ranks)
        embed = Embed(title="🏆🏆🏆 League 🏆🏆🏆", color=Color.blue())
        embed.set_thumbnail(
            url="https://preview.redd.it/m41lh2t0yvj81.png?auto=webp&s=2b3438c08fc12cdb496a7c5f716533c746932604",
        )
        embed.add_field(
            name="=-------------------------------------------=",
            value=rank_table,
            inline=False,
        )
        return embed


if __name__ == "__main__":  # pragma: no cover
    league = League(DBConnection())
    league.get_league_scores()
    info = league.get_league_info()
    print(league.get_ranks_table(info))
