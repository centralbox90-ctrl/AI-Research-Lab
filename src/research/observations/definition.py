from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ObservationDefinition:
    """
    Воспроизводимое описание того,
    какое событие считается наблюдением.
    """

    id: str
    question_id: str
    hypothesis_id: str
    title: str
    description: str
    observation_type: str

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("id must not be empty")

        if not self.question_id.strip():
            raise ValueError("question_id must not be empty")

        if not self.hypothesis_id.strip():
            raise ValueError("hypothesis_id must not be empty")

        if not self.title.strip():
            raise ValueError("title must not be empty")

        if not self.description.strip():
            raise ValueError("description must not be empty")

        if not self.observation_type.strip():
            raise ValueError(
                "observation_type must not be empty"
            )