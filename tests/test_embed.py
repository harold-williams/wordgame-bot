from unittest.mock import MagicMock
from wordgame_bot.embed import FAILURE_THUMBNAILS, SUCCESS_THUMBNAILS, QuordleMessage, WordleMessage
from discord import Colour, Embed, User
from wordgame_bot.quordle import QuordleAttempt

from wordgame_bot.wordle import WordleAttempt

def test_wordle_embed_good_score(user: User):
    attempt = WordleAttempt(info=MagicMock(day=4, score=2), guesses=MagicMock())
    embed = WordleMessage().create_embed(attempt, user)
    embed_values = embed.to_dict()
    assert embed_values["author"]["name"] == "WordleParser"
    assert embed_values["title"] == "🤠 Wordle Submission 🤠"
    assert embed_values["thumbnail"]["url"] in SUCCESS_THUMBNAILS

def test_wordle_embed_bad_score(user: User):
    attempt = WordleAttempt(info=MagicMock(day=4, score=8), guesses=MagicMock())
    embed = WordleMessage().create_embed(attempt, user)
    embed_values = embed.to_dict()
    assert embed_values["author"]["name"] == "WordleParser"
    assert embed_values["title"] == "🤠 Wordle Submission 🤠"
    assert embed_values["thumbnail"]["url"] in FAILURE_THUMBNAILS

def test_quordle_embed_good_score(user: User):
    attempt = QuordleAttempt(info=MagicMock(day=4, score=18), guesses=MagicMock())
    embed = QuordleMessage().create_embed(attempt, user)
    embed_values = embed.to_dict()
    assert embed_values["author"]["name"] == "QuordleParser"
    assert embed_values["title"] == "🧠 Quordle Submission 🧠"
    assert embed_values["thumbnail"]["url"] in SUCCESS_THUMBNAILS

def test_quordle_embed_bad_score(user: User):
    attempt = QuordleAttempt(info=MagicMock(day=4, score=31), guesses=MagicMock())
    embed = QuordleMessage().create_embed(attempt, user)
    embed_values = embed.to_dict()
    assert embed_values["author"]["name"] == "QuordleParser"
    assert embed_values["title"] == "🧠 Quordle Submission 🧠"
    assert embed_values["thumbnail"]["url"] in FAILURE_THUMBNAILS