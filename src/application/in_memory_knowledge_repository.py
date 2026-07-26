from src.research.knowledge_applicability_query import (
    KnowledgeApplicabilityQuery,
)
from src.research.knowledge_contradiction import (
    KnowledgeContradiction,
)
from src.research.knowledge_item import KnowledgeItem
from src.research.knowledge_repository import (
    KnowledgeItemConflictError,
    KnowledgeRevisionSequenceError,
)
from src.research.knowledge_revision import (
    KnowledgeRevision,
)


class InMemoryKnowledgeRepository:
    """
    Append-only in-memory storage for KnowledgeRevision history.
    """

    def __init__(self) -> None:
        self._revisions: dict[
            str,
            dict[int, KnowledgeRevision],
        ] = {}
        self._contradictions: dict[
            str,
            KnowledgeContradiction,
        ] = {}

    def save(
        self,
        revision: KnowledgeRevision,
    ) -> None:
        if not isinstance(
            revision,
            KnowledgeRevision,
        ):
            raise TypeError(
                "revision must be a KnowledgeRevision"
            )

        item_id = revision.item.id
        version = revision.item.version
        revisions = self._revisions.get(item_id)

        if revisions is None:
            if version != 1:
                raise KnowledgeRevisionSequenceError(
                    item_id=item_id,
                    expected_version=1,
                    incoming_version=version,
                )

            self._revisions[item_id] = {
                version: revision,
            }
            return

        existing = revisions.get(version)

        if existing is not None:
            if existing != revision:
                raise KnowledgeItemConflictError(
                    item_id=item_id,
                    version=version,
                    existing_fingerprint=(
                        existing.fingerprint
                    ),
                    incoming_fingerprint=(
                        revision.fingerprint
                    ),
                )

            return

        latest_version = max(revisions)
        expected_version = latest_version + 1

        if version != expected_version:
            raise KnowledgeRevisionSequenceError(
                item_id=item_id,
                expected_version=expected_version,
                incoming_version=version,
            )

        latest_revision = revisions[
            latest_version
        ]

        if (
            revision.valid_from
            <= latest_revision.valid_from
        ):
            raise ValueError(
                "revision valid_from must be later "
                "than the latest stored revision"
            )

        revisions[version] = revision

    def get(
        self,
        item_id: str,
    ) -> KnowledgeItem | None:
        revisions = self._revisions.get(
            self._normalize_item_id(item_id)
        )

        if not revisions:
            return None

        return revisions[max(revisions)].item

    def get_version(
        self,
        item_id: str,
        version: int,
    ) -> KnowledgeRevision | None:
        revisions = self._revisions.get(
            self._normalize_item_id(item_id)
        )
        normalized_version = (
            self._normalize_version(version)
        )

        if revisions is None:
            return None

        return revisions.get(normalized_version)

    def history(
        self,
        item_id: str,
    ) -> tuple[KnowledgeRevision, ...]:
        revisions = self._revisions.get(
            self._normalize_item_id(item_id)
        )

        if revisions is None:
            return ()

        return tuple(
            revisions[version]
            for version in sorted(revisions)
        )

    def list_all(
        self,
    ) -> tuple[KnowledgeItem, ...]:
        return tuple(
            self._revisions[item_id][
                max(self._revisions[item_id])
            ].item
            for item_id in sorted(self._revisions)
        )

    def find_applicable(
        self,
        query: KnowledgeApplicabilityQuery,
    ) -> tuple[KnowledgeItem, ...]:
        if not isinstance(
            query,
            KnowledgeApplicabilityQuery,
        ):
            raise TypeError(
                "query must be a "
                "KnowledgeApplicabilityQuery"
            )

        return tuple(
            item
            for item in self.list_all()
            if query.matches(item)
        )

    def save_contradiction(
        self,
        contradiction: KnowledgeContradiction,
    ) -> None:
        if not isinstance(
            contradiction,
            KnowledgeContradiction,
        ):
            raise TypeError(
                "contradiction must be a "
                "KnowledgeContradiction"
            )

        for item in contradiction.items:
            revisions = self._revisions.get(
                item.id
            )
            stored_revision = (
                None
                if revisions is None
                else revisions.get(item.version)
            )

            if (
                stored_revision is None
                or stored_revision.item.fingerprint
                != item.fingerprint
            ):
                raise ValueError(
                    "contradiction items must "
                    "reference stored knowledge versions"
                )

        self._contradictions.setdefault(
            contradiction.fingerprint,
            contradiction,
        )

    def list_contradictions(
        self,
    ) -> tuple[KnowledgeContradiction, ...]:
        return tuple(
            sorted(
                self._contradictions.values(),
                key=self._contradiction_sort_key,
            )
        )

    def contradictions_for(
        self,
        item_id: str,
    ) -> tuple[KnowledgeContradiction, ...]:
        normalized_item_id = (
            self._normalize_item_id(item_id)
        )

        return tuple(
            contradiction
            for contradiction
            in self.list_contradictions()
            if any(
                item.id == normalized_item_id
                for item in contradiction.items
            )
        )

    @staticmethod
    def _contradiction_sort_key(
        contradiction: KnowledgeContradiction,
    ) -> tuple[object, ...]:
        return (
            tuple(
                (
                    item.id,
                    item.version,
                    item.fingerprint,
                )
                for item in contradiction.items
            ),
            contradiction.reason,
            contradiction.fingerprint,
        )

    @staticmethod
    def _normalize_item_id(
        value: object,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                "item_id must be a string"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "item_id must not be empty"
            )

        return normalized

    @staticmethod
    def _normalize_version(
        value: object,
    ) -> int:
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
        ):
            raise TypeError(
                "version must be an integer"
            )

        if value < 1:
            raise ValueError(
                "version must be positive"
            )

        return value
