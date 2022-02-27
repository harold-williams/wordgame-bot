import pytest
from wordgame_bot.wordle import WordleAttemptParser

@pytest.fixture
def parser():
    return WordleAttemptParser("")
