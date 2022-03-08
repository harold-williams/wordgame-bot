import pytest
from discord import Message, User
from unittest.mock import AsyncMock, MagicMock, create_autospec
from wordgame_bot.bot import WordgameBot

from wordgame_bot.leaderboard import Leaderboard
from wordgame_bot.wordle import WordleAttemptParser

def create_user(username: str, id: int) -> User:
    data = {
        "username": username,
        "id": id,
        "discriminator": "test",
        "avatar": None,
    }
    return User(state=None, data=data)

@pytest.fixture
def user():
    return create_user("test", 1)

@pytest.fixture
def leaderboard():
    Leaderboard.create_table = MagicMock()
    return Leaderboard(MagicMock())

@pytest.fixture
def valid_message():
    message = AsyncMock()
    message.author = create_user("test", 1)
    message.channel.id = 944748500787269653
    return message

@pytest.fixture
def invalid_message():
    message = AsyncMock()
    message.channel.id = -1
    return message

@pytest.fixture
def mock_parser():
    mock_parser = MagicMock()
    mock_parser.parse.return_value = MagicMock()
    return mock_parser