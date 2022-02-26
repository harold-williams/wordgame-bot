from abc import ABC, abstractclassmethod


class Attempt(ABC):
    pass

class AttemptParser(ABC):

    @abstractclassmethod
    def parse():
        pass
