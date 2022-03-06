from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import os
from typing import Tuple

# from dotenv import load_dotenv
from discord import Color, Embed, User
import psycopg2

from wordgame_bot.quordle import QuordleAttempt
from wordgame_bot.wordle import WordleAttempt

# load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
CREATE_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS attempts (
    user_id BIGINT,
    day INTEGER,
    score INTEGER,
    mode CHAR(1),
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
Scores = Tuple[int, str, int]

@dataclass
class AttemptDuplication(Exception):
    username: str
    day: int

class Leaderboard:
    def __init__(self, conn) -> None:
        self.conn = conn
        self.scores = []
        self.create_table()
    
    def create_table(self):
        with self.conn.cursor() as curs:
            curs.execute(CREATE_TABLE_SCHEMA)
            self.conn.commit()

    def insert_wordle(self, attempt: WordleAttempt, user: User):
        self.verify_valid_user(user)
        try:
            with self.conn.cursor() as curs:
                curs.execute(
                    "INSERT INTO attempts(user_id, mode, day, score) VALUES (%s, %s, %s, %s)",
                    (
                        user.id,
                        'W',
                        attempt.day,
                        attempt.score,
                    )
                )
                self.conn.commit()
        except psycopg2.errors.UniqueViolation:
            self.conn.rollback()
            raise AttemptDuplication(user.name, attempt.day)

    def insert_submission(self, attempt: QuordleAttempt, user: User):
        self.verify_valid_user(user)
        try:
            with self.conn.cursor() as curs:
                curs.execute(
                    "INSERT INTO attempts(user_id, mode, day, score) VALUES (%s, %s, %s, %s)",
                    (
                        user.id,
                        'Q',
                        attempt.day,
                        attempt.score,
                    )
                )
                self.conn.commit()
        except psycopg2.errors.UniqueViolation:
            self.conn.rollback()
            raise AttemptDuplication(user.name, attempt.day)

    def verify_valid_user(self, user: User):
        with self.conn.cursor() as curs:
            print(curs.fetchone)
            curs.execute("SELECT * FROM users WHERE user_id = %s", (user.id,))
            if curs.fetchone() is not None:
                return
            else:
                curs.execute(
                    "INSERT INTO users(user_id, username) VALUES (%s, %s)",
                    (
                        user.id,
                        user.name
                    )
                )
                self.conn.commit()
        return

    def get_leaderboard(self):
        self.retrieve_scores()
        return self.format_leaderboard()

    def retrieve_scores(self) -> list[Scores]:
        self.scores = []
        with self.conn.cursor() as curs:
            curs.execute(LEADERBOARD_SCHEMA)
            self.conn.commit()
            for entry in curs:
                self.scores.append(entry)

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
        rank_strings = {
            1: '🥇',
            2: '🥈',
            3: '🥉'
        }
        return rank_strings.get(rank, str(rank))

    def format_leaderboard(self) -> Embed:
        ranks = self.get_ranks_table()
        embed = Embed(
            title = "🏆 Leaderboard 🏆",
            color = Color.blue()
        )
        embed.set_author(name="OfficialStandings", icon_url="https://static.wikia.nocookie.net/spongebob/images/9/96/The_Two_Faces_of_Squidward_174.png/revision/latest?cb=20200923005328")
        embed.set_thumbnail(url="https://images.cdn.circlesix.co/image/2/1200/700/5/uploads/articles/podium-2-546b7f7bf3c7b.jpeg")
        embed.add_field(name="Ranks", value=ranks, inline=False)
        embed.set_footer(text="Quordle: https://www.quordle.com/#/\nWordle: https://www.nytimes.com/games/wordle/index.html")
        return embed


@contextmanager
def connect_to_leaderboard() -> Leaderboard:
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    yield Leaderboard(conn)
    conn.close()
    
        
if __name__ == "__main__":
    with connect_to_leaderboard() as lb:
        print(lb.get_leaderboard())