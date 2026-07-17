from typing import Protocol


class IdGenerator(Protocol):

    def generate(self) -> str:
        ...
