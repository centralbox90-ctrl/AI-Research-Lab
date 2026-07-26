from src.research.knowledge_item import KnowledgeItem
from src.research.knowledge_relation import (
    KnowledgeRelation,
    KnowledgeRelationType,
)
from src.research.knowledge_relation_repository import (
    KnowledgeRelationReferenceError,
)
from src.research.knowledge_repository import (
    KnowledgeRepository,
)


class InMemoryKnowledgeRelationRepository:
    """
    Append-only in-memory storage for typed knowledge relations.
    """

    def __init__(
        self,
        knowledge_repository: KnowledgeRepository,
    ) -> None:
        if not isinstance(
            knowledge_repository,
            KnowledgeRepository,
        ):
            raise TypeError(
                "knowledge_repository must implement "
                "KnowledgeRepository"
            )

        self._knowledge_repository = (
            knowledge_repository
        )
        self._relations: dict[
            str,
            KnowledgeRelation,
        ] = {}

    def save(
        self,
        relation: KnowledgeRelation,
    ) -> None:
        if not isinstance(
            relation,
            KnowledgeRelation,
        ):
            raise TypeError(
                "relation must be a "
                "KnowledgeRelation"
            )

        self._validate_endpoint(
            endpoint="source",
            item=relation.source,
        )
        self._validate_endpoint(
            endpoint="target",
            item=relation.target,
        )

        self._relations.setdefault(
            relation.fingerprint,
            relation,
        )

    def list_all(
        self,
    ) -> tuple[KnowledgeRelation, ...]:
        return tuple(
            sorted(
                self._relations.values(),
                key=self._relation_sort_key,
            )
        )

    def outgoing(
        self,
        item_id: str,
        *,
        version: int | None = None,
        relation_type: (
            KnowledgeRelationType | None
        ) = None,
    ) -> tuple[KnowledgeRelation, ...]:
        normalized_item_id = (
            self._normalize_item_id(item_id)
        )
        normalized_version = (
            self._normalize_optional_version(
                version
            )
        )
        normalized_relation_type = (
            self._normalize_optional_relation_type(
                relation_type
            )
        )

        return tuple(
            relation
            for relation in self.list_all()
            if self._matches_endpoint(
                relation.source,
                item_id=normalized_item_id,
                version=normalized_version,
            )
            and self._matches_relation_type(
                relation,
                normalized_relation_type,
            )
        )

    def incoming(
        self,
        item_id: str,
        *,
        version: int | None = None,
        relation_type: (
            KnowledgeRelationType | None
        ) = None,
    ) -> tuple[KnowledgeRelation, ...]:
        normalized_item_id = (
            self._normalize_item_id(item_id)
        )
        normalized_version = (
            self._normalize_optional_version(
                version
            )
        )
        normalized_relation_type = (
            self._normalize_optional_relation_type(
                relation_type
            )
        )

        return tuple(
            relation
            for relation in self.list_all()
            if self._matches_endpoint(
                relation.target,
                item_id=normalized_item_id,
                version=normalized_version,
            )
            and self._matches_relation_type(
                relation,
                normalized_relation_type,
            )
        )

    def relations_for(
        self,
        item_id: str,
        *,
        version: int | None = None,
        relation_type: (
            KnowledgeRelationType | None
        ) = None,
    ) -> tuple[KnowledgeRelation, ...]:
        normalized_item_id = (
            self._normalize_item_id(item_id)
        )
        normalized_version = (
            self._normalize_optional_version(
                version
            )
        )
        normalized_relation_type = (
            self._normalize_optional_relation_type(
                relation_type
            )
        )

        return tuple(
            relation
            for relation in self.list_all()
            if (
                self._matches_endpoint(
                    relation.source,
                    item_id=normalized_item_id,
                    version=normalized_version,
                )
                or self._matches_endpoint(
                    relation.target,
                    item_id=normalized_item_id,
                    version=normalized_version,
                )
            )
            and self._matches_relation_type(
                relation,
                normalized_relation_type,
            )
        )

    def _validate_endpoint(
        self,
        *,
        endpoint: str,
        item: KnowledgeItem,
    ) -> None:
        revision = (
            self._knowledge_repository.get_version(
                item.id,
                item.version,
            )
        )

        if (
            revision is None
            or revision.item.fingerprint
            != item.fingerprint
        ):
            raise KnowledgeRelationReferenceError(
                endpoint=endpoint,
                item_id=item.id,
                version=item.version,
            )

    @staticmethod
    def _relation_sort_key(
        relation: KnowledgeRelation,
    ) -> tuple[object, ...]:
        return (
            relation.source.id,
            relation.source.version,
            relation.source.fingerprint,
            relation.relation_type.value,
            relation.target.id,
            relation.target.version,
            relation.target.fingerprint,
            relation.reason,
            relation.fingerprint,
        )

    @staticmethod
    def _matches_endpoint(
        item: KnowledgeItem,
        *,
        item_id: str,
        version: int | None,
    ) -> bool:
        return (
            item.id == item_id
            and (
                version is None
                or item.version == version
            )
        )

    @staticmethod
    def _matches_relation_type(
        relation: KnowledgeRelation,
        relation_type: (
            KnowledgeRelationType | None
        ),
    ) -> bool:
        return (
            relation_type is None
            or relation.relation_type
            is relation_type
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
    def _normalize_optional_version(
        value: object,
    ) -> int | None:
        if value is None:
            return None

        if (
            not isinstance(value, int)
            or isinstance(value, bool)
        ):
            raise TypeError(
                "version must be an integer "
                "or None"
            )

        if value < 1:
            raise ValueError(
                "version must be positive"
            )

        return value

    @staticmethod
    def _normalize_optional_relation_type(
        value: object,
    ) -> KnowledgeRelationType | None:
        if value is None:
            return None

        if not isinstance(
            value,
            KnowledgeRelationType,
        ):
            raise TypeError(
                "relation_type must be a "
                "KnowledgeRelationType or None"
            )

        return value
