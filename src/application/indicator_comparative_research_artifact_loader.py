from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any


class IndicatorComparativeResearchArtifactLoader:
    """
    Loads and validates comparative research artifacts from JSON.

    The loader returns an application-safe dictionary. It does not
    reconstruct research domain objects or access persistent storage.
    """

    _ARTIFACT_TYPE = (
        "indicator_comparative_research"
    )
    _ARTIFACT_VERSION = 1
    _REQUIRED_SECTIONS = frozenset(
        {
            "indicator",
            "market",
            "dataset",
            "outcome_specification",
            "analysis",
        }
    )

    def load(
        self,
        path: str | Path,
    ) -> dict[str, Any]:
        artifact_path = Path(path)

        try:
            source = artifact_path.read_text(
                encoding="utf-8",
            )
        except OSError as error:
            raise ValueError(
                "unable to read comparative research "
                f"artifact: {artifact_path}"
            ) from error

        try:
            payload = json.loads(source)
        except JSONDecodeError as error:
            raise ValueError(
                "invalid comparative research "
                f"artifact JSON: {error.msg}"
            ) from error

        return self.from_dict(payload)

    def from_dict(
        self,
        payload: Any,
    ) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError(
                "comparative research artifact JSON "
                "must contain an object"
            )

        if payload.get("artifact_type") != (
            self._ARTIFACT_TYPE
        ):
            raise ValueError(
                "artifact_type must be "
                "'indicator_comparative_research'"
            )

        artifact_version = payload.get(
            "artifact_version"
        )

        if (
            not isinstance(artifact_version, int)
            or isinstance(artifact_version, bool)
            or artifact_version
            != self._ARTIFACT_VERSION
        ):
            raise ValueError(
                "artifact_version must be 1"
            )

        missing_sections = sorted(
            self._REQUIRED_SECTIONS
            - payload.keys()
        )

        if missing_sections:
            raise ValueError(
                "missing comparative research "
                "artifact sections: "
                + ", ".join(missing_sections)
            )

        for section_name in sorted(
            self._REQUIRED_SECTIONS
        ):
            if not isinstance(
                payload[section_name],
                dict,
            ):
                raise ValueError(
                    f"{section_name} must be an object"
                )

        return dict(payload)
