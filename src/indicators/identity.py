from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IndicatorIdentity:
    id: str
    symbol: str
    name: str
    version: int = 1

    def __post_init__(self) -> None:
        indicator_id = self.id.strip()
        symbol = self.symbol.strip()
        name = self.name.strip()

        if not indicator_id:
            raise ValueError("id must not be empty.")

        if not symbol:
            raise ValueError("symbol must not be empty.")

        if not name:
            raise ValueError("name must not be empty.")

        if isinstance(self.version, bool) or not isinstance(
            self.version,
            int,
        ):
            raise TypeError("version must be an integer.")

        if self.version < 1:
            raise ValueError(
                "version must be greater than zero."
            )

        object.__setattr__(self, "id", indicator_id)
        object.__setattr__(self, "symbol", symbol)
        object.__setattr__(self, "name", name)