from __future__ import annotations

from abc import ABC, abstractclassmethod, abstractproperty
from dataclasses import dataclass

from wordgame_bot.guess import Guesses, GuessInfo


@dataclass
class Attempt(ABC):
    info: GuessInfo
    guesses: Guesses | list[Guesses]

    @abstractproperty
    def gamemode(self):
        pass

    @abstractproperty
    def maxscore(self):
        pass

    @property
    def score(self):
        return self.maxscore - self.info.score


class AttemptParser(ABC):
    @abstractclassmethod
    def parse(self):
        pass
