from src.application.artifact_lineage import ArtifactLineage


def test_artifact_lineage_creation():

    lineage = ArtifactLineage(
        parent_artifact_id="artifact-001",
        lineage_type="derived_from",
        change_description="Added ADX confirmation feature",
        created_from_experiment="experiment-002",
    )

    assert lineage.parent_artifact_id == "artifact-001"
    assert lineage.lineage_type == "derived_from"
    assert (
        lineage.change_description
        == "Added ADX confirmation feature"
    )
    assert (
        lineage.created_from_experiment
        == "experiment-002"
    )