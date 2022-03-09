from __future__ import annotations
from contextlib import contextmanager

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Generator

import psycopg2
from discord import Color, Embed, User

from wordgame_bot.leaderboard import DATABASE_URL

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
        submission_date >= %s
    GROUP BY
        user_id, submission_date
    ORDER BY total DESC
) scores
INNER JOIN users
    ON scores.user_id = users.user_id;
"""


@dataclass
class League:
    conn: psycopg2.connection
    League_length: timedelta = timedelta(days=7)
    scores: dict[int, int] = field(default_factory=dict)

    @property
    def start_day(self):
        today = datetime.today()
        return today - timedelta(days=today.weekday())

    def get_league_table(self):
        self.get_league_scores()
        return self.format_league()

    def get_today_scores(self):
        self.scores = {}
        with self.get_cursor() as curs:
            curs.execute(SCORES, datetime.today())
            retrieved_scores = curs.fetchall()
            for (user_id, score) in retrieved_scores:
                self.scores[user_id] = score
            self.conn.commit()

    def get_league_scores(self):
        self.table = {}
        with self.get_cursor() as curs:
            curs.execute(LEAGUE_TABLE, self.start_day)
            retrieved_scores = curs.fetchall()
            for (user_id, day, score) in retrieved_scores:
                self.table.setdefault(user_id, {})[day] = score
            self.conn.commit()

    def get_latest_league_ranks(self):
        ranks = [(username, sum(scores.values())) for username, scores in self.table.items()]
        ranks.sort(key=lambda x: x[1], reverse=True)
        return [(rank + 1, user, score) for rank, (user, score) in enumerate(ranks) if score != 0]

    def get_previous_league_ranks(self):
        ranks = [
            (
                username,
                sum([score for day, score in scores.items() if day != datetime.today()])
            )
            for username, scores in self.table.items()
        ]
        ranks.sort(key=lambda x: x[1], reverse=True)
        return [(rank + 1, user, score) for rank, (user, score) in enumerate(ranks) if score != 0]

    @contextmanager
    def get_cursor(self) -> Generator[psycopg2.cursor]:
        with self.conn.cursor() as cursor:
            yield cursor

    def get_ranks_table(self):
        self.scores.sort(key=lambda x: x.get(datetime.today), reverse=True)
        ranks = "\n".join(
            f"{self.get_rank_value(rank)}. {user} -- {score}"
            for rank, (user, score) in enumerate(self.scores)
        )
        return ranks

    @staticmethod
    def get_rank_value(rank):
        rank += 1
        rank_strings = {
            1: '🥇',
            2: '🥈',
            3: '🥉'
        }
        return rank_strings.get(rank, str(rank))

    def format_league(self) -> Embed:
        ranks = self.get_ranks_table()
        embed = Embed(
            title = "🏆🏆🏆 League 🏆🏆🏆\n--- Today's Scores ---",
            color = Color.blue()
        )
        embed.set_author(name="OfficialStandings", icon_url="https://static.wikia.nocookie.net/spongebob/images/9/96/The_Two_Faces_of_Squidward_174.png/revision/latest?cb=20200923005328")
        embed.set_thumbnail(url="https://images.cdn.circlesix.co/image/2/1200/700/5/uploads/articles/podium-2-546b7f7bf3c7b.jpeg")
        embed.add_field(name="Ranks", value=ranks, inline=False)
        embed.set_footer(text="Quordle: https://www.quordle.com/#/\nWordle: https://www.nytimes.com/games/wordle/index.html")
        return embed

@contextmanager
def connect_to_league() -> Generator[League]:
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        yield League(conn)
    finally:
        conn.close()
