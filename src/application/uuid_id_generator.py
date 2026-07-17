from uuid import uuid4


class UuidIdGenerator:

    def generate(self) -> str:
        return str(uuid4())
