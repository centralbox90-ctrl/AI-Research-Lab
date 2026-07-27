from src.research.knowledge_gap import (
    KnowledgeGap,
    KnowledgeGapType,
)
from src.research.knowledge_graph_snapshot import (
    KnowledgeGraphSnapshot,
)
from src.research.knowledge_item import KnowledgeItem
from src.research.knowledge_relation import (
    KnowledgeRelation,
    KnowledgeRelationType,
)


_GAP_TYPE_ORDER = {
    KnowledgeGapType.ISOLATED_ITEM: 0,
    KnowledgeGapType.UNSUPPORTED_ITEM: 1,
    KnowledgeGapType.UNRESOLVED_CONTRADICTION: 2,
}


def _item_key(
    item: KnowledgeItem,
) -> tuple[str, int, str]:
    return (
        item.id,
        item.version,
        item.fingerprint,
    )


def _gap_key(
    gap: KnowledgeGap,
) -> tuple[object, ...]:
    return (
        _GAP_TYPE_ORDER[gap.gap_type],
        tuple(
            _item_key(item)
            for item in gap.items
        ),
        gap.applicability,
        gap.reason,
        gap.fingerprint,
    )


def _is_incident(
    item: KnowledgeItem,
    relation: KnowledgeRelation,
) -> bool:
    return (
        relation.source.fingerprint
        == item.fingerprint
        or relation.target.fingerprint
        == item.fingerprint
    )


def _is_supported(
    item: KnowledgeItem,
    relations: tuple[
        KnowledgeRelation,
        ...,
    ],
    active_fingerprints: set[str],
) -> bool:
    for relation in relations:
        if (
            relation.relation_type
            is KnowledgeRelationType.SUPPORTS
            and relation.target.fingerprint
            == item.fingerprint
            and relation.source.fingerprint
            in active_fingerprints
        ):
            return True

        if (
            relation.relation_type
            is KnowledgeRelationType.DERIVED_FROM
            and relation.source.fingerprint
            == item.fingerprint
            and relation.target.fingerprint
            in active_fingerprints
        ):
            return True

    return False


def _applicability_overlap(
    left: KnowledgeItem,
    right: KnowledgeItem,
) -> tuple[str, ...]:
    left_terms = {
        term.casefold()
        for term in left.applicability
    }
    right_terms = {
        term.casefold()
        for term in right.applicability
    }

    return tuple(
        sorted(left_terms & right_terms)
    )


class KnowledgeGapDetector:
    """
    Detects deterministic topology gaps in a graph snapshot.
    """

    def detect(
        self,
        snapshot: KnowledgeGraphSnapshot,
    ) -> tuple[KnowledgeGap, ...]:
        if not isinstance(
            snapshot,
            KnowledgeGraphSnapshot,
        ):
            raise TypeError(
                "snapshot must be a "
                "KnowledgeGraphSnapshot"
            )

        superseded_fingerprints = {
            relation.target.fingerprint
            for relation in snapshot.relations
            if (
                relation.relation_type
                is KnowledgeRelationType.SUPERSEDES
            )
        }
        active_items = tuple(
            item
            for item in snapshot.items
            if (
                item.fingerprint
                not in superseded_fingerprints
            )
        )
        active_fingerprints = {
            item.fingerprint
            for item in active_items
        }
        gaps: dict[str, KnowledgeGap] = {}

        for item in active_items:
            is_incident = any(
                _is_incident(
                    item,
                    relation,
                )
                for relation
                in snapshot.relations
            )

            if not is_incident:
                gap = KnowledgeGap(
                    gap_type=(
                        KnowledgeGapType
                        .ISOLATED_ITEM
                    ),
                    items=(item,),
                    applicability=(
                        item.applicability
                    ),
                    reason=(
                        "Knowledge item has no "
                        "graph relations."
                    ),
                    snapshot_fingerprint=(
                        snapshot.fingerprint
                    ),
                )
                gaps.setdefault(
                    gap.fingerprint,
                    gap,
                )
                continue

            if not _is_supported(
                item,
                snapshot.relations,
                active_fingerprints,
            ):
                gap = KnowledgeGap(
                    gap_type=(
                        KnowledgeGapType
                        .UNSUPPORTED_ITEM
                    ),
                    items=(item,),
                    applicability=(
                        item.applicability
                    ),
                    reason=(
                        "Knowledge item has no "
                        "incoming supports or "
                        "outgoing derived_from "
                        "relation."
                    ),
                    snapshot_fingerprint=(
                        snapshot.fingerprint
                    ),
                )
                gaps.setdefault(
                    gap.fingerprint,
                    gap,
                )

        for relation in snapshot.relations:
            if (
                relation.relation_type
                is not KnowledgeRelationType.CONTRADICTS
                or relation.source.fingerprint
                not in active_fingerprints
                or relation.target.fingerprint
                not in active_fingerprints
            ):
                continue

            applicability = (
                _applicability_overlap(
                    relation.source,
                    relation.target,
                )
            )

            if not applicability:
                continue

            gap = KnowledgeGap(
                gap_type=(
                    KnowledgeGapType
                    .UNRESOLVED_CONTRADICTION
                ),
                items=(
                    relation.source,
                    relation.target,
                ),
                applicability=applicability,
                reason=(
                    "Contradicting knowledge "
                    "items have not been "
                    "superseded."
                ),
                snapshot_fingerprint=(
                    snapshot.fingerprint
                ),
            )
            gaps.setdefault(
                gap.fingerprint,
                gap,
            )

        return tuple(
            sorted(
                gaps.values(),
                key=_gap_key,
            )
        )
