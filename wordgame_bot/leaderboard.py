from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Tuple

import psycopg2
from discord import Colour, Embed, User

from wordgame_bot.attempt import Attempt
from wordgame_bot.db import DBConnection

DATABASE_URL = os.getenv("DATABASE_URL")
CREATE_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS attempts (
    user_id BIGINT,
    day INTEGER,
    score INTEGER,
    mode CHAR(1),
    submission_date DATE,
    PRIMARY KEY (user_id, mode, day)
);
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(200)
)
"""
LEADERBOARD_SCHEMA = """
SELECT username, total
FROM (
    SELECT
        user_id,
        SUM (score) AS total
    FROM
        attempts AS a
    GROUP BY
        user_id
    ORDER BY total DESC
) scores
INNER JOIN users
    ON scores.user_id = users.user_id;
"""
Score = Tuple[str, int]


@dataclass
class AttemptDuplication(Exception):
    username: str
    day: int


@dataclass
class Leaderboard:
    db: DBConnection
    scores: list[Score] = field(default_factory=list)

    def __post_init__(self):
        self.create_table()

    def create_table(self):
        with self.db.get_cursor() as curs:
            curs.execute(CREATE_TABLE_SCHEMA)
            self.db.commit()

    def insert_submission(self, attempt: Attempt, user: User):
        self.verify_valid_user(user)
        try:
            with self.db.get_cursor() as curs:
                curs.execute(
                    (
                        "INSERT INTO attempts(user_id, mode, day, score, submission_date) "
                        "VALUES (%s, %s, %s, %s, %s)"
                    ),
                    (
                        user.id,
                        attempt.gamemode,
                        attempt.info.day,
                        attempt.score,
                        datetime.today(),
                    ),
                )
                self.db.commit()
        except psycopg2.errors.UniqueViolation:
            self.db.rollback()
            raise AttemptDuplication(user.name, attempt.info.day)

    def verify_valid_user(self, user: User):
        with self.db.get_cursor() as curs:
            curs.execute("SELECT * FROM users WHERE user_id = %s", (user.id,))
            if curs.fetchone() is not None:
                return
            else:
                curs.execute(
                    "INSERT INTO users(user_id, username) VALUES (%s, %s)",
                    (user.id, user.name),
                )
                self.db.commit()
        return

    def get_leaderboard(self):
        self.retrieve_scores()
        return self.format_leaderboard()

    def retrieve_scores(self):
        self.scores = []
        with self.db.get_cursor() as curs:
            curs.execute(LEADERBOARD_SCHEMA)
            retrieved_scores = curs.fetchall()
            for score in retrieved_scores:
                self.scores.append(score)
            self.db.commit()

    def get_ranks_table(self):
        self.scores.sort(key=lambda x: x[1], reverse=True)
        ranks = "\n".join(
            f"{self.get_rank_value(rank)}. {user} -- {score}"
            for rank, (user, score) in enumerate(self.scores)
        )
        return ranks

    @staticmethod
    def get_rank_value(rank):
        rank += 1
        rank_strings = {1: "🥇", 2: "🥈", 3: "🥉"}
        return rank_strings.get(rank, str(rank))

    def format_leaderboard(self) -> Embed:
        ranks = self.get_ranks_table()
        embed = Embed(title="🏆 Leaderboard 🏆", color=Colour.blue())
        embed.set_author(
            name="OfficialStandings",
            icon_url="https://static.wikia.nocookie.net/spongebob/images/9/96/The_Two_Faces_of_Squidward_174.png/revision/latest?cb=20200923005328",
        )
        embed.set_thumbnail(
            url="https://images.cdn.circlesix.co/image/2/1200/700/5/uploads/articles/podium-2-546b7f7bf3c7b.jpeg",
        )
        embed.add_field(name="Ranks", value=ranks, inline=False)
        embed.set_footer(
            text="Quordle: https://www.quordle.com/#/\nWordle: https://www.nytimes.com/games/wordle/index.html",
        )
        return embed
