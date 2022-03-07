from abc import ABC, abstractclassmethod, abstractproperty
from dataclasses import dataclass

from wordgame_bot.guess import GuessInfo, Guesses

@dataclass
class Attempt(ABC):
    info: GuessInfo
    guesses: Guesses

    @abstractproperty
    def score():
        pass

    @abstractproperty
    def gamemode():
        pass

class AttemptParser(ABC):

    @abstractclassmethod
    def parse():
        pass
