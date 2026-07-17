from pathlib import Path
from typing import Any, Protocol

from flask import (
    Flask,
    abort,
    render_template_string,
    request,
)

from src.application import (
    GetStoredResearchArtifact,
    ListStoredResearchCycles,
)
from src.application.artifact_comparison import (
    ArtifactComparison,
)
from src.application.artifact_comparison_input_extractor import (
    ArtifactComparisonInputExtractor,
)
from src.application.compare_stored_research_artifacts import (
    CompareStoredResearchArtifacts,
)
from src.storage import (
    RESEARCH_CYCLE_DATABASE_PATH,
    SqliteResearchCycleStore,
)


class StoredResearchCycleLister(Protocol):
    def execute(self) -> list[str]:
        ...


class StoredResearchArtifactGetter(Protocol):
    def execute(
        self,
        result_id: str,
    ) -> dict[str, Any] | None:
        ...


class StoredResearchArtifactComparer(Protocol):
    def execute(
        self,
        artifact_a_result_id: str,
        artifact_b_result_id: str,
    ) -> ArtifactComparison:
        ...


INDEX_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>AI Research Lab</title>
</head>
<body>
    <main>
        <h1>AI Research Lab</h1>
        <p>Research artifact interface is running.</p>
        <nav aria-label="Quick navigation">
            <p>
                <a href="#dashboard">
                    Dashboard
                </a>
                |
                <a href="#filters">
                    Filters
                </a>
                |
                <a href="#comparison">
                    Comparison
                </a>
                |
                <a href="#artifacts">
                    Artifacts
                </a>
            </p>
        </nav>
         <section id="filters">
            <h2>Filter and sort research artifacts</h2>
        <section id="dashboard">
            <h2>Research dashboard</h2>

            <dl>
                <dt>Total artifacts</dt>
                <dd>{{ dashboard_statistics.total }}</dd>

                <dt>Root artifacts</dt>
                <dd>{{ dashboard_statistics.root_count }}</dd>

                <dt>Child artifacts</dt>
                <dd>{{ dashboard_statistics.child_count }}</dd>

                <dt>Orphan artifacts</dt>
                <dd>{{ dashboard_statistics.orphan_count }}</dd>

                <dt>Average confidence</dt>
                <dd>
                    {% if (
                        dashboard_statistics.average_confidence
                        is not none
                    ) %}
                        {{
                            format_display_value(
                                dashboard_statistics
                                .average_confidence
                            )
                        }}
                    {% else %}
                        Not available
                    {% endif %}
                </dd>
            </dl>

            <h3>Artifacts by symbol</h3>

            {% if dashboard_statistics.symbols %}
                <ul>
                    {% for symbol, count in (
                        dashboard_statistics.symbols.items()
                    ) %}
                        <li>
                            {{ symbol }}: {{ count }}
                        </li>
                    {% endfor %}
                </ul>
            {% else %}
                <p>No symbol statistics are available.</p>
            {% endif %}

            <h3>Artifacts by timeframe</h3>

            {% if dashboard_statistics.timeframes %}
                <ul>
                    {% for timeframe, count in (
                        dashboard_statistics.timeframes.items()
                    ) %}
                        <li>
                            {{ timeframe }}: {{ count }}
                        </li>
                    {% endfor %}
                </ul>
            {% else %}
                <p>No timeframe statistics are available.</p>
            {% endif %}
        </section>
            <form action="{{ url_for('index') }}" method="get">
                <p>
                    <label for="filter-symbol">
                        Symbol
                    </label>

                    <input
                        id="filter-symbol"
                        name="symbol"
                        value="{{ filters.symbol }}"
                        placeholder="BTCUSDT"
                    >
                </p>

                <p>
                    <label for="filter-timeframe">
                        Timeframe
                    </label>

                    <input
                        id="filter-timeframe"
                        name="timeframe"
                        value="{{ filters.timeframe }}"
                        placeholder="1h"
                    >
                </p>

                <p>
                    <label for="filter-hypothesis">
                        Hypothesis
                    </label>

                    <input
                        id="filter-hypothesis"
                        name="hypothesis"
                        value="{{ filters.hypothesis }}"
                        placeholder="Williams"
                    >
                </p>

                <p>
                    <label for="filter-lineage-type">
                        Lineage type
                    </label>

                    <input
                        id="filter-lineage-type"
                        name="lineage_type"
                        value="{{ filters.lineage_type }}"
                        placeholder="hypothesis_refinement"
                    >
                </p>

                <p>
                    <label for="sort-by">
                        Sort by
                    </label>

                    <select
                        id="sort-by"
                        name="sort_by"
                    >
                        <option
                            value="created_at"
                            {% if sorting.sort_by == "created_at" %}
                                selected
                            {% endif %}
                        >
                            Created at
                        </option>

                        <option
                            value="confidence"
                            {% if sorting.sort_by == "confidence" %}
                                selected
                            {% endif %}
                        >
                            Confidence
                        </option>

                        <option
                            value="symbol"
                            {% if sorting.sort_by == "symbol" %}
                                selected
                            {% endif %}
                        >
                            Symbol
                        </option>

                        <option
                            value="lineage_depth"
                            {% if sorting.sort_by == "lineage_depth" %}
                                selected
                            {% endif %}
                        >
                            Lineage depth
                        </option>
                    </select>
                </p>

                <p>
                    <label for="sort-direction">
                        Sort direction
                    </label>

                    <select
                        id="sort-direction"
                        name="sort_direction"
                    >
                        <option
                            value="descending"
                            {% if (
                                sorting.sort_direction
                                == "descending"
                            ) %}
                                selected
                            {% endif %}
                        >
                            Descending
                        </option>

                        <option
                            value="ascending"
                            {% if (
                                sorting.sort_direction
                                == "ascending"
                            ) %}
                                selected
                            {% endif %}
                        >
                            Ascending
                        </option>
                   </select>
                </p>

                <p>
    <label for="page-size">
        Items per page
    </label>

    <select
        id="page-size"
        name="page_size"
    >
        {% for size in [5, 10, 25, 50] %}
            <option
                value="{{ size }}"
                {% if pagination.page_size == size %}
                    selected
                {% endif %}
            >
                {{ size }}
            </option>
        {% endfor %}
    </select>
</p>

                <button type="submit">
                    Apply filters and sorting
                </button>

                <a href="{{ url_for('index') }}">
                    Clear filters and sorting
                </a>
            </form>

                       {% if filters_are_active %}
                <p>Showing {{ pagination.total_items }} of {{ all_artifacts|length }} research artifacts.</p>
            {% endif %}
        </section>

        <section id="comparison">
            <h2>Compare research artifacts</h2>

            <form action="{{ url_for('compare_artifacts') }}" method="get">
                <p>
                    <label for="artifact-a-result-id">
                        Previous artifact
                    </label>

                    <select
                        id="artifact-a-result-id"
                        name="artifact_a_result_id"
                        required
                    >
                        <option value="">
                            Select previous artifact
                        </option>

                        {% for artifact in all_artifacts %}
                            <option value="{{ artifact.result_id }}">
                                {{ artifact.symbol }}
                                ·
                                {{ artifact.timeframe }}
                                ·
                                {{ artifact.result_id }}
                            </option>
                        {% endfor %}
                    </select>
                </p>

                <p>
                    <label for="artifact-b-result-id">
                        Current artifact
                    </label>

                    <select
                        id="artifact-b-result-id"
                        name="artifact_b_result_id"
                        required
                    >
                        <option value="">
                            Select current artifact
                        </option>

                        {% for artifact in all_artifacts %}
                            <option value="{{ artifact.result_id }}">
                                {{ artifact.symbol }}
                                ·
                                {{ artifact.timeframe }}
                                ·
                                {{ artifact.result_id }}
                            </option>
                        {% endfor %}
                    </select>
                </p>

                <button
                    type="submit"
                    {% if all_artifacts|length < 2 %}disabled{% endif %}
                >
                    Compare artifacts
                </button>

                {% if all_artifacts|length < 2 %}
                    <p>
                        At least two stored research artifacts are required
                        for comparison.
                    </p>
                {% endif %}
            </form>
        </section>

        <section>
            <h2>Research lineage tree</h2>

            {% if lineage_tree %}
                <ul>
                    {% for node in lineage_tree recursive %}
                        <li>
                            <article>
                                <h3>
                                    <a href="{{ url_for(
                                        'artifact_details',
                                        result_id=node.result_id
                                    ) }}">
                                        {{ node.symbol }}
                                        ·
                                        {{ node.timeframe }}
                                    </a>
                                </h3>

                                <p>{{ node.hypothesis }}</p>

                                <dl>
                                    <dt>Artifact ID</dt>
                                    <dd>
                                        {{
                                            node.artifact_id
                                            or "Not available"
                                        }}
                                    </dd>

                                    <dt>Result ID</dt>
                                    <dd>{{ node.result_id }}</dd>

                                    <dt>Lineage type</dt>
                                    <dd>
                                        {{
                                            node.lineage_type
                                            or "Not available"
                                        }}
                                    </dd>

                                    <dt>Depth</dt>
                                    <dd>{{ node.depth }}</dd>

                                    <dt>Children</dt>
                                    <dd>{{ node.children|length }}</dd>
                                </dl>
                            </article>

                            {% if node.children %}
                                <ul>
                                    {{ loop(node.children) }}
                                </ul>
                            {% endif %}
                        </li>
                    {% endfor %}
                </ul>
            {% else %}
                <p>No research lineage is available.</p>
            {% endif %}

            {% if orphan_artifacts %}
                <h3>Artifacts with missing or filtered parents</h3>

                <ul>
                    {% for artifact in orphan_artifacts %}
                        <li>
                            <a href="{{ url_for(
                                'artifact_details',
                                result_id=artifact.result_id
                            ) }}">
                                {{ artifact.symbol }}
                                ·
                                {{ artifact.timeframe }}
                                ·
                                {{ artifact.artifact_id }}
                            </a>

                            <p>
                                Parent:
                                {{ artifact.parent_artifact_id }}
                            </p>
                        </li>
                    {% endfor %}
                </ul>
            {% endif %}
        </section>

        <section id="artifacts">
            <h2>Research artifacts</h2>

            {% if artifacts %}
                <ol>
                    {% for artifact in artifacts %}
                        <li>
                            <article>
                                <h3>
                                    <a href="{{ url_for(
                                        'artifact_details',
                                        result_id=artifact.result_id
                                    ) }}">
                                        {{ artifact.symbol }}
                                        ·
                                        {{ artifact.timeframe }}
                                    </a>
                                </h3>

                                <p>{{ artifact.hypothesis }}</p>

                                <dl>
                                    <dt>Confidence</dt>
                                    <dd>
                                        {{
                                            format_display_value(
                                                artifact.confidence
                                            )
                                            if artifact.confidence is not none
                                            else "Not available"
                                        }}
                                    </dd>

                                    <dt>Created</dt>
                                    <dd>{{ artifact.created_at }}</dd>

                                    <dt>Result ID</dt>
                                    <dd>{{ artifact.result_id }}</dd>

                                    <dt>Artifact ID</dt>
                                    <dd>
                                        {{
                                            artifact.artifact_id
                                            or "Not available"
                                        }}
                                    </dd>

                                    <dt>Lineage type</dt>
                                    <dd>
                                        {{
                                            artifact.lineage_type
                                            or "Not available"
                                        }}
                                    </dd>

                                    <dt>Lineage depth</dt>
                                    <dd>{{ artifact.depth }}</dd>

                                    <dt>Parent artifact</dt>
                                    <dd>
                                        {% if artifact.parent_result_id %}
                                            <a href="{{ url_for(
                                                'artifact_details',
                                                result_id=(
                                                    artifact
                                                    .parent_result_id
                                                )
                                            ) }}">
                                                {{
                                                    artifact
                                                    .parent_artifact_id
                                                }}
                                            </a>
                                        {% elif artifact.parent_artifact_id %}
                                            {{
                                                artifact.parent_artifact_id
                                            }}
                                        {% else %}
                                            No parent artifact
                                        {% endif %}
                                    </dd>
                                </dl>
                            </article>
                        </li>
                    {% endfor %}
                </ol>
            {% elif filters_are_active %}
                <p>
                    No research artifacts match the active filters.
                </p>
            {% else %}
                <p>No stored research artifacts.</p>
            {% endif %}
{% if pagination.total_items %}
    <nav aria-label="Research artifact pagination">
        <p>
            Page {{ pagination.page }}
            of {{ pagination.total_pages }}
        </p>

        {% if pagination.has_previous %}
            <a href="{{ url_for(
                'index',
                symbol=filters.symbol,
                timeframe=filters.timeframe,
                hypothesis=filters.hypothesis,
                lineage_type=filters.lineage_type,
                sort_by=sorting.sort_by,
                sort_direction=sorting.sort_direction,
                page=pagination.previous_page,
                page_size=pagination.page_size
            ) }}">
                Previous page
            </a>
        {% endif %}

        {% if pagination.has_next %}
            <a href="{{ url_for(
                'index',
                symbol=filters.symbol,
                timeframe=filters.timeframe,
                hypothesis=filters.hypothesis,
                lineage_type=filters.lineage_type,
                sort_by=sorting.sort_by,
                sort_direction=sorting.sort_direction,
                page=pagination.next_page,
                page_size=pagination.page_size
            ) }}">
                Next page
            </a>
        {% endif %}
    </nav>
{% endif %}
        </section>
    </main>
</body>
</html>
"""


ARTIFACT_DETAILS_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Research artifact</title>
</head>
<body>
    <main>
        <p>
            <a href="{{ url_for('index') }}">
                Back to research artifacts
            </a>
        </p>

        <h1>Research artifact</h1>

        <section>
            <h2>Artifact identity</h2>

            <dl>
                <dt>Result ID</dt>
                <dd>{{ details.result_id }}</dd>

                <dt>Artifact ID</dt>
                <dd>{{ details.artifact_id or "Not available" }}</dd>

                <dt>Created at</dt>
                <dd>{{ details.created_at or "Not available" }}</dd>

                <dt>Executor type</dt>
                <dd>
                    {{ details.executor_type or "Not available" }}
                </dd>

                <dt>Data source</dt>
                <dd>{{ details.data_source or "Not available" }}</dd>
            </dl>
        </section>

        <section>
            <h2>Research lineage</h2>

            <dl>
                <dt>Parent artifact ID</dt>
                <dd>
                    {% if details.parent_result_id %}
                        <a href="{{ url_for(
                            'artifact_details',
                            result_id=details.parent_result_id
                        ) }}">
                            {{ details.parent_artifact_id }}
                        </a>
                    {% elif details.parent_artifact_id %}
                        {{ details.parent_artifact_id }}
                    {% else %}
                        No parent artifact
                    {% endif %}
                </dd>

                <dt>Lineage type</dt>
                <dd>{{ details.lineage_type or "Not available" }}</dd>

                <dt>Change description</dt>
                <dd>
                    {{
                        details.lineage_change_description
                        or "Not available"
                    }}
                </dd>

                <dt>Created from experiment</dt>
                <dd>
                    {{
                        details.created_from_experiment
                        or "Not available"
                    }}
                </dd>
            </dl>

            <h3>Child artifacts</h3>

            {% if child_artifacts %}
                <ul>
                    {% for child in child_artifacts %}
                        <li>
                            <a href="{{ url_for(
                                'artifact_details',
                                result_id=child.result_id
                            ) }}">
                                {{ child.symbol }}
                                ·
                                {{ child.timeframe }}
                                ·
                                {{ child.artifact_id }}
                            </a>

                            <p>{{ child.hypothesis }}</p>
                        </li>
                    {% endfor %}
                </ul>
            {% else %}
                <p>No child artifacts.</p>
            {% endif %}
        </section>

        <section>
            <h2>Artifact history</h2>

            {% if details.history %}
                <table>
                    <thead>
                        <tr>
                            <th>Event</th>
                            <th>Artifact ID</th>
                            <th>Previous artifact ID</th>
                            <th>Description</th>
                            <th>Created at</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for entry in details.history %}
                            <tr>
                                <td>
                                    {{
                                        entry.event_type
                                        or "Not available"
                                    }}
                                </td>
                                <td>
                                    {{
                                        entry.artifact_id
                                        or "Not available"
                                    }}
                                </td>
                                <td>
                                    {{
                                        entry.previous_artifact_id
                                        or "Not available"
                                    }}
                                </td>
                                <td>
                                    {{
                                        entry.description
                                        or "Not available"
                                    }}
                                </td>
                                <td>
                                    {{
                                        entry.created_at
                                        or "Not available"
                                    }}
                                </td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <p>No artifact history is available.</p>
            {% endif %}
        </section>

        <section>
            <h2>Research specification</h2>

            <dl>
                <dt>Question</dt>
                <dd>{{ details.question or "Not available" }}</dd>

                <dt>Hypothesis</dt>
                <dd>{{ details.hypothesis or "Not available" }}</dd>

                <dt>Expected result</dt>
                <dd>
                    {{ details.expected_result or "Not available" }}
                </dd>

                <dt>Experiment</dt>
                <dd>{{ details.experiment or "Not available" }}</dd>

                <dt>Symbol</dt>
                <dd>{{ details.symbol or "Not available" }}</dd>

                <dt>Timeframe</dt>
                <dd>{{ details.timeframe or "Not available" }}</dd>
            </dl>
        </section>

        <section>
            <h2>Evidence metrics</h2>

            {% if details.evidence_metrics %}
                <table>
                    <thead>
                        <tr>
                            <th>Metric</th>
                            <th>Value</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for metric_name, metric_value in (
                            details.evidence_metrics.items()
                        ) %}
                            <tr>
                                <td>{{ metric_name }}</td>
                                <td>
                                    {{
                                        format_display_value(
                                            metric_value
                                        )
                                    }}
                                </td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <p>No evidence metrics are available.</p>
            {% endif %}
        </section>

        <section>
            <h2>Evidence strength</h2>

            <dl>
                <dt>Score</dt>
                <dd>
                    {{
                        format_display_value(
                            details.evidence_strength_score
                        )
                        if (
                            details.evidence_strength_score
                            is not none
                        )
                        else "Not available"
                    }}
                </dd>

                <dt>Level</dt>
                <dd>
                    {{
                        details.evidence_strength_level
                        or "Not available"
                    }}
                </dd>

                <dt>Evaluated</dt>
                <dd>
                    {{
                        details.evidence_strength_evaluated
                        if (
                            details.evidence_strength_evaluated
                            is not none
                        )
                        else "Not available"
                    }}
                </dd>
            </dl>

            {% if details.evidence_strength_warnings %}
                <h3>Warnings</h3>

                <ul>
                    {% for warning in (
                        details.evidence_strength_warnings
                    ) %}
                        <li>{{ warning }}</li>
                    {% endfor %}
                </ul>
            {% endif %}
        </section>

        <section>
            <h2>Experiment evaluation</h2>

            <dl>
                <dt>Valid result</dt>
                <dd>
                    {{
                        details.result_is_valid
                        if details.result_is_valid is not none
                        else "Not available"
                    }}
                </dd>

                <dt>Evaluation strength</dt>
                <dd>
                    {{
                        details.evaluation_strength
                        or "Not available"
                    }}
                </dd>
            </dl>

            {% if details.evaluation_warnings %}
                <h3>Warnings</h3>

                <ul>
                    {% for warning in details.evaluation_warnings %}
                        <li>{{ warning }}</li>
                    {% endfor %}
                </ul>
            {% endif %}
        </section>

        <section>
            <h2>Statistical evaluation</h2>

            <dl>
                <dt>Evaluated</dt>
                <dd>
                    {{
                        details.statistics_evaluated
                        if details.statistics_evaluated is not none
                        else "Not available"
                    }}
                </dd>

                <dt>Sample size</dt>
                <dd>
                    {{
                        details.sample_size
                        if details.sample_size is not none
                        else "Not available"
                    }}
                </dd>

                <dt>Mean</dt>
                <dd>
                    {{
                        format_display_value(
                            details.statistical_mean
                        )
                        if details.statistical_mean is not none
                        else "Not available"
                    }}
                </dd>

                <dt>Standard deviation</dt>
                <dd>
                    {{
                        format_display_value(
                            details.standard_deviation
                        )
                        if details.standard_deviation is not none
                        else "Not available"
                    }}
                </dd>

                <dt>Standard error</dt>
                <dd>
                    {{
                        format_display_value(
                            details.standard_error
                        )
                        if details.standard_error is not none
                        else "Not available"
                    }}
                </dd>

                <dt>Confidence interval</dt>
                <dd>
                    {% if (
                        details.confidence_interval_lower is not none
                        and
                        details.confidence_interval_upper is not none
                    ) %}
                        {{
                            format_display_value(
                                details.confidence_interval_lower
                            )
                        }}
                        –
                        {{
                            format_display_value(
                                details.confidence_interval_upper
                            )
                        }}
                    {% else %}
                        Not available
                    {% endif %}
                </dd>

                <dt>Confidence level</dt>
                <dd>
                    {{
                        format_display_value(
                            details.confidence_level
                        )
                        if details.confidence_level is not none
                        else "Not available"
                    }}
                </dd>

                <dt>Statistically significant</dt>
                <dd>
                    {{
                        details.statistically_significant
                        if (
                            details.statistically_significant
                            is not none
                        )
                        else "Not available"
                    }}
                </dd>

                <dt>P-value</dt>
                <dd>
                    {{
                        format_display_value(
                            details.p_value
                        )
                        if details.p_value is not none
                        else "Not available"
                    }}
                </dd>

                <dt>Effect size</dt>
                <dd>
                    {{
                        format_display_value(
                            details.effect_size
                        )
                        if details.effect_size is not none
                        else "Not available"
                    }}
                </dd>
            </dl>

            {% if details.statistical_warnings %}
                <h3>Warnings</h3>

                <ul>
                    {% for warning in details.statistical_warnings %}
                        <li>{{ warning }}</li>
                    {% endfor %}
                </ul>
            {% endif %}
        </section>

        <section>
            <h2>Hypothesis decision</h2>

            <dl>
                <dt>Decision</dt>
                <dd>
                    {{
                        details.hypothesis_decision
                        or "Not available"
                    }}
                </dd>

                <dt>Supported</dt>
                <dd>
                    {{
                        details.hypothesis_supported
                        if details.hypothesis_supported is not none
                        else "Not available"
                    }}
                </dd>

                <dt>Decision confidence</dt>
                <dd>
                    {{
                        format_display_value(
                            details.decision_confidence
                        )
                        if details.decision_confidence is not none
                        else "Not available"
                    }}
                </dd>

                <dt>Decision reason</dt>
                <dd>
                    {{
                        details.decision_reason
                        or "Not available"
                    }}
                </dd>
            </dl>

            {% if details.decision_failed_requirements %}
                <h3>Failed requirements</h3>

                <ul>
                    {% for requirement in (
                        details.decision_failed_requirements
                    ) %}
                        <li>{{ requirement }}</li>
                    {% endfor %}
                </ul>
            {% endif %}

            {% if details.decision_warnings %}
                <h3>Warnings</h3>

                <ul>
                    {% for warning in details.decision_warnings %}
                        <li>{{ warning }}</li>
                    {% endfor %}
                </ul>
            {% endif %}
        </section>

        <section>
            <h2>Conclusion</h2>

            <dl>
                <dt>Statement</dt>
                <dd>
                    {{
                        details.conclusion_statement
                        or "Not available"
                    }}
                </dd>

                <dt>Supported</dt>
                <dd>
                    {{
                        details.conclusion_supported
                        if details.conclusion_supported is not none
                        else "Not available"
                    }}
                </dd>

                <dt>Confidence</dt>
                <dd>
                    {{
                        format_display_value(
                            details.conclusion_confidence
                        )
                        if details.conclusion_confidence is not none
                        else "Not available"
                    }}
                </dd>

                <dt>Provisional</dt>
                <dd>
                    {{
                        details.conclusion_is_provisional
                        if (
                            details.conclusion_is_provisional
                            is not none
                        )
                        else "Not available"
                    }}
                </dd>

                <dt>Basis</dt>
                <dd>
                    {{
                        details.conclusion_basis
                        or "Not available"
                    }}
                </dd>
            </dl>
        </section>

        <section>
            <h2>Next research action</h2>

            <dl>
                <dt>Selected</dt>
                <dd>
                    {{
                        details.next_experiment_selected
                        if (
                            details.next_experiment_selected
                            is not none
                        )
                        else "Not available"
                    }}
                </dd>

                <dt>Action</dt>
                <dd>
                    {{
                        details.next_experiment_action
                        or "Not available"
                    }}
                </dd>

                <dt>Priority</dt>
                <dd>
                    {{
                        details.next_experiment_priority
                        or "Not available"
                    }}
                </dd>

                <dt>Reason</dt>
                <dd>
                    {{
                        details.next_experiment_reason
                        or "Not available"
                    }}
                </dd>

                <dt>Target requirement</dt>
                <dd>
                    {{
                        details.next_experiment_target_requirement
                        or "Not available"
                    }}
                </dd>
            </dl>

            {% if details.next_experiment_recommendations %}
                <h3>Recommendations</h3>

                <ul>
                    {% for recommendation in (
                        details.next_experiment_recommendations
                    ) %}
                        <li>{{ recommendation }}</li>
                    {% endfor %}
                </ul>
            {% endif %}

            {% if details.next_experiment_warnings %}
                <h3>Warnings</h3>

                <ul>
                    {% for warning in (
                        details.next_experiment_warnings
                    ) %}
                        <li>{{ warning }}</li>
                    {% endfor %}
                </ul>
            {% endif %}
        </section>
    </main>
</body>
</html>
"""


COMPARISON_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Research artifact comparison</title>
</head>
<body>
    <main>
        <p>
            <a href="{{ url_for('index') }}">
                Back to research artifacts
            </a>
        </p>

        <h1>Research artifact comparison</h1>

        <dl>
            <dt>Previous artifact</dt>
            <dd>{{ comparison.artifact_a_id }}</dd>

            <dt>Current artifact</dt>
            <dd>{{ comparison.artifact_b_id }}</dd>
        </dl>

        <section>
            <h2>Hypothesis evolution</h2>

            <dl>
                <dt>Previous hypothesis</dt>
                <dd>
                    {{
                        comparison
                        .hypothesis_evolution
                        .previous_hypothesis
                        or "Not available"
                    }}
                </dd>

                <dt>Current hypothesis</dt>
                <dd>
                    {{
                        comparison
                        .hypothesis_evolution
                        .current_hypothesis
                    }}
                </dd>

                <dt>Change reason</dt>
                <dd>
                    {{
                        comparison
                        .hypothesis_evolution
                        .change_reason
                        or "No change"
                    }}
                </dd>
            </dl>
        </section>

        <section>
            <h2>Evidence metric changes</h2>

            {% if comparison.evidence_evolution.metric_deltas %}
                <table>
                    <thead>
                        <tr>
                            <th>Metric</th>
                            <th>Previous</th>
                            <th>Current</th>
                            <th>Absolute delta</th>
                            <th>Direction</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for delta in (
                            comparison
                            .evidence_evolution
                            .metric_deltas
                        ) %}
                            <tr>
                                <td>{{ delta.metric_name }}</td>
                                <td>
                                    {{
                                        format_display_value(
                                            delta.previous_value
                                        )
                                        if delta.previous_value is not none
                                        else "Not available"
                                    }}
                                </td>
                                <td>
                                    {{
                                        format_display_value(
                                            delta.current_value
                                        )
                                        if delta.current_value is not none
                                        else "Not available"
                                    }}
                                </td>
                                <td>
                                    {{
                                        format_display_value(
                                            delta.absolute_delta
                                        )
                                        if delta.absolute_delta is not none
                                        else "Not comparable"
                                    }}
                                </td>
                                <td>{{ delta.direction }}</td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <p>No metric changes are available.</p>
            {% endif %}

            <p>
                Evidence change reason:
                {{
                    comparison
                    .evidence_evolution
                    .change_reason
                    or "No change"
                }}
            </p>
        </section>

        <section>
            <h2>Confidence evolution</h2>

            <dl>
                <dt>Previous confidence</dt>
                <dd>
                    {{
                        format_display_value(
                            comparison
                            .confidence_evolution
                            .previous_confidence
                        )
                    }}
                </dd>

                <dt>Current confidence</dt>
                <dd>
                    {{
                        format_display_value(
                            comparison
                            .confidence_evolution
                            .current_confidence
                        )
                    }}
                </dd>

                <dt>Change reason</dt>
                <dd>
                    {{
                        comparison
                        .confidence_evolution
                        .change_reason
                        or "No change"
                    }}
                </dd>
            </dl>
        </section>
    </main>
</body>
</html>
"""


def format_display_value(
    value: Any,
) -> Any:
    if isinstance(value, float):
        return round(
            value,
            6,
        )

    return value


def as_dictionary(
    value: Any,
) -> dict[str, Any]:
    if isinstance(value, dict):
        return value

    return {}


def as_list(
    value: Any,
) -> list[Any]:
    if isinstance(value, list):
        return value

    return []


def first_available(
    data: dict[str, Any],
    *keys: str,
) -> Any:
    for key in keys:
        value = data.get(key)

        if value is not None:
            return value

    return None


def build_artifact_summary(
    result_id: str,
    artifact: dict[str, Any] | None,
) -> dict[str, Any]:
    if artifact is None:
        return {
            "result_id": result_id,
            "artifact_id": None,
            "parent_artifact_id": None,
            "parent_result_id": None,
            "lineage_type": None,
            "depth": 0,
            "symbol": "Unknown symbol",
            "timeframe": "Unknown timeframe",
            "hypothesis": "Hypothesis not available",
            "confidence": None,
            "created_at": "Not available",
        }

    metadata = as_dictionary(
        artifact.get("metadata")
    )

    specification = as_dictionary(
        artifact.get("specification")
    )

    lineage = as_dictionary(
        artifact.get("lineage")
    )

    cycle = as_dictionary(
        artifact.get("cycle")
    )

    evidence_strength_evaluation = as_dictionary(
        cycle.get("evidence_strength_evaluation")
    )

    hypothesis = first_available(
        specification,
        "hypothesis_description",
        "hypothesis_title",
    )

    return {
        "result_id": result_id,
        "artifact_id": metadata.get("artifact_id"),
        "parent_artifact_id": lineage.get(
            "parent_artifact_id"
        ),
        "parent_result_id": None,
        "lineage_type": lineage.get("lineage_type"),
        "depth": 0,
        "symbol": (
            specification.get("symbol")
            or "Unknown symbol"
        ),
        "timeframe": (
            specification.get("timeframe")
            or "Unknown timeframe"
        ),
        "hypothesis": (
            hypothesis
            or "Hypothesis not available"
        ),
        "confidence": evidence_strength_evaluation.get(
            "score"
        ),
        "created_at": (
            metadata.get("created_at")
            or "Not available"
        ),
    }


def assign_lineage_depths(
    artifacts: list[dict[str, Any]],
) -> None:
    artifact_by_id = {
        artifact["artifact_id"]: artifact
        for artifact in artifacts
        if artifact.get("artifact_id")
    }

    depth_cache: dict[str, int] = {}

    def resolve_depth(
        artifact: dict[str, Any],
        active_path: set[str],
    ) -> int:
        artifact_id = artifact.get("artifact_id")

        if not artifact_id:
            return 0

        if artifact_id in depth_cache:
            return depth_cache[artifact_id]

        if artifact_id in active_path:
            depth_cache[artifact_id] = 0
            return 0

        parent_artifact_id = artifact.get(
            "parent_artifact_id"
        )

        if not parent_artifact_id:
            depth_cache[artifact_id] = 0
            return 0

        parent_artifact = artifact_by_id.get(
            parent_artifact_id
        )

        if parent_artifact is None:
            depth_cache[artifact_id] = 0
            return 0

        depth = 1 + resolve_depth(
            parent_artifact,
            {
                *active_path,
                artifact_id,
            },
        )

        depth_cache[artifact_id] = depth

        return depth

    for artifact in artifacts:
        artifact["depth"] = resolve_depth(
            artifact,
            set(),
        )


def build_artifact_index(
    result_ids: list[str],
    artifact_getter: StoredResearchArtifactGetter | None,
) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []

    for result_id in result_ids:
        artifact = (
            artifact_getter.execute(result_id)
            if artifact_getter is not None
            else None
        )

        artifacts.append(
            build_artifact_summary(
                result_id=result_id,
                artifact=artifact,
            )
        )

    result_id_by_artifact_id = {
        artifact["artifact_id"]: artifact["result_id"]
        for artifact in artifacts
        if artifact["artifact_id"]
    }

    for artifact in artifacts:
        parent_artifact_id = artifact[
            "parent_artifact_id"
        ]

        artifact["parent_result_id"] = (
            result_id_by_artifact_id.get(
                parent_artifact_id
            )
            if parent_artifact_id
            else None
        )

    assign_lineage_depths(
        artifacts=artifacts,
    )

    return artifacts


def filter_artifacts(
    artifacts: list[dict[str, Any]],
    *,
    symbol: str = "",
    timeframe: str = "",
    hypothesis: str = "",
    lineage_type: str = "",
) -> list[dict[str, Any]]:
    normalized_symbol = symbol.strip().casefold()
    normalized_timeframe = timeframe.strip().casefold()
    normalized_hypothesis = hypothesis.strip().casefold()
    normalized_lineage_type = lineage_type.strip().casefold()

    filtered_artifacts: list[dict[str, Any]] = []

    for artifact in artifacts:
        artifact_symbol = str(
            artifact.get("symbol") or ""
        ).casefold()

        artifact_timeframe = str(
            artifact.get("timeframe") or ""
        ).casefold()

        artifact_hypothesis = str(
            artifact.get("hypothesis") or ""
        ).casefold()

        artifact_lineage_type = str(
            artifact.get("lineage_type") or ""
        ).casefold()

        if (
            normalized_symbol
            and normalized_symbol not in artifact_symbol
        ):
            continue

        if (
            normalized_timeframe
            and normalized_timeframe
            not in artifact_timeframe
        ):
            continue

        if (
            normalized_hypothesis
            and normalized_hypothesis
            not in artifact_hypothesis
        ):
            continue

        if (
            normalized_lineage_type
            and normalized_lineage_type
            not in artifact_lineage_type
        ):
            continue

        filtered_artifacts.append(artifact)

    return filtered_artifacts


def sort_artifacts(
    artifacts: list[dict[str, Any]],
    *,
    sort_by: str = "created_at",
    descending: bool = True,
) -> list[dict[str, Any]]:
    if sort_by == "symbol":
        return sorted(
            artifacts,
            key=lambda artifact: str(
                artifact.get("symbol") or ""
            ).casefold(),
            reverse=descending,
        )

    if sort_by == "confidence":
        return sorted(
            artifacts,
            key=lambda artifact: (
                artifact.get("confidence")
                if artifact.get("confidence") is not None
                else float("-inf")
            ),
            reverse=descending,
        )

    if sort_by == "lineage_depth":
        return sorted(
            artifacts,
            key=lambda artifact: artifact.get(
                "depth",
                0,
            ),
            reverse=descending,
        )

    return sorted(
        artifacts,
        key=lambda artifact: str(
            artifact.get("created_at") or ""
        ),
        reverse=descending,
    )

def paginate_artifacts(
    artifacts: list[dict[str, Any]],
    *,
    page: int = 1,
    page_size: int = 10,
) -> dict[str, Any]:
    normalized_page_size = max(
        page_size,
        1,
    )

    total_items = len(artifacts)

    total_pages = max(
        (
            total_items
            + normalized_page_size
            - 1
        )
        // normalized_page_size,
        1,
    )

    normalized_page = min(
        max(page, 1),
        total_pages,
    )

    start_index = (
        normalized_page - 1
    ) * normalized_page_size

    end_index = (
        start_index
        + normalized_page_size
    )

    return {
        "items": artifacts[
            start_index:end_index
        ],
        "page": normalized_page,
        "page_size": normalized_page_size,
        "total_items": total_items,
        "total_pages": total_pages,
        "has_previous": normalized_page > 1,
        "has_next": normalized_page < total_pages,
        "previous_page": (
            normalized_page - 1
            if normalized_page > 1
            else None
        ),
        "next_page": (
            normalized_page + 1
            if normalized_page < total_pages
            else None
        ),
    }
def build_dashboard_statistics(
    artifacts: list[dict[str, Any]],
) -> dict[str, Any]:
    total = len(
        artifacts,
    )

    root_count = 0
    child_count = 0
    orphan_count = 0

    confidence_values: list[float] = []

    symbols: dict[str, int] = {}
    timeframes: dict[str, int] = {}

    for artifact in artifacts:

        if (
            artifact.get(
                "parent_artifact_id"
            )
            is None
        ):
            root_count += 1
        else:
            child_count += 1

        if (
            artifact.get(
                "parent_result_id"
            )
            is None
            and artifact.get(
                "parent_artifact_id"
            )
            is not None
        ):
            orphan_count += 1

        confidence = artifact.get(
            "confidence"
        )

        if isinstance(
            confidence,
            (
                int,
                float,
            ),
        ):
            confidence_values.append(
                float(
                    confidence,
                )
            )

        symbol = artifact.get(
            "symbol"
        )

        if symbol:
            symbols[
                symbol
            ] = (
                symbols.get(
                    symbol,
                    0,
                )
                + 1
            )

        timeframe = artifact.get(
            "timeframe"
        )

        if timeframe:
            timeframes[
                timeframe
            ] = (
                timeframes.get(
                    timeframe,
                    0,
                )
                + 1
            )

    average_confidence = None

    if confidence_values:
        average_confidence = round(
            sum(
                confidence_values,
            )
            / len(
                confidence_values,
            ),
            4,
        )

    return {
        "total": total,
        "root_count": root_count,
        "child_count": child_count,
        "orphan_count": orphan_count,
        "average_confidence": (
            average_confidence
        ),
        "symbols": dict(
            sorted(
                symbols.items(),
            )
        ),
        "timeframes": dict(
            sorted(
                timeframes.items(),
            )
        ),
    }
def build_lineage_tree(
    artifacts: list[dict[str, Any]],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    artifact_by_id = {
        artifact["artifact_id"]: artifact
        for artifact in artifacts
        if artifact["artifact_id"]
    }

    children_by_parent_id: dict[
        str,
        list[dict[str, Any]],
    ] = {}

    root_artifacts: list[dict[str, Any]] = []
    orphan_artifacts: list[dict[str, Any]] = []

    for artifact in artifacts:
        artifact_id = artifact.get("artifact_id")

        if not artifact_id:
            continue

        parent_artifact_id = artifact[
            "parent_artifact_id"
        ]

        if not parent_artifact_id:
            root_artifacts.append(artifact)
            continue

        if parent_artifact_id not in artifact_by_id:
            orphan_artifacts.append(artifact)
            continue

        children_by_parent_id.setdefault(
            parent_artifact_id,
            [],
        ).append(artifact)

    visited_artifact_ids: set[str] = set()

    def build_node(
        artifact: dict[str, Any],
        depth: int,
        active_path: set[str],
    ) -> dict[str, Any]:
        artifact_id = artifact.get("artifact_id")

        node = {
            **artifact,
            "depth": depth,
            "children": [],
            "has_cycle": False,
        }

        if not artifact_id:
            return node

        if artifact_id in active_path:
            node["has_cycle"] = True
            return node

        if artifact_id in visited_artifact_ids:
            return node

        visited_artifact_ids.add(artifact_id)

        next_active_path = {
            *active_path,
            artifact_id,
        }

        node["children"] = [
            build_node(
                artifact=child,
                depth=depth + 1,
                active_path=next_active_path,
            )
            for child in children_by_parent_id.get(
                artifact_id,
                [],
            )
        ]

        return node

    lineage_tree = [
        build_node(
            artifact=root_artifact,
            depth=0,
            active_path=set(),
        )
        for root_artifact in root_artifacts
    ]

    remaining_artifacts = [
        artifact
        for artifact in artifacts
        if (
            artifact.get("artifact_id")
            and artifact["artifact_id"]
            not in visited_artifact_ids
            and artifact not in orphan_artifacts
        )
    ]

    orphan_artifacts.extend(
        remaining_artifacts
    )

    return (
        lineage_tree,
        orphan_artifacts,
    )


def normalize_history(
    history: Any,
) -> list[dict[str, Any]]:
    normalized_history: list[dict[str, Any]] = []

    for entry in as_list(history):
        if not isinstance(entry, dict):
            continue

        normalized_history.append(
            {
                "artifact_id": entry.get("artifact_id"),
                "previous_artifact_id": entry.get(
                    "previous_artifact_id"
                ),
                "event_type": entry.get("event_type"),
                "description": entry.get("description"),
                "created_at": entry.get("created_at"),
            }
        )

    return normalized_history


def build_artifact_details(
    result_id: str,
    artifact: dict[str, Any],
) -> dict[str, Any]:
    metadata = as_dictionary(
        artifact.get("metadata")
    )

    specification = as_dictionary(
        artifact.get("specification")
    )

    lineage = as_dictionary(
        artifact.get("lineage")
    )

    cycle = as_dictionary(
        artifact.get("cycle")
    )

    evidence = as_dictionary(
        cycle.get("evidence")
    )

    evidence_metrics = as_dictionary(
        evidence.get("data")
    )

    evaluation = as_dictionary(
        cycle.get("evaluation")
    )

    statistical_evaluation = as_dictionary(
        cycle.get("statistical_evaluation")
    )

    evidence_strength_evaluation = as_dictionary(
        cycle.get("evidence_strength_evaluation")
    )

    hypothesis_decision = as_dictionary(
        cycle.get("hypothesis_decision")
    )

    conclusion = as_dictionary(
        cycle.get("conclusion")
    )

    next_experiment_selection = as_dictionary(
        cycle.get("next_experiment_selection")
    )

    hypothesis = first_available(
        specification,
        "hypothesis_description",
        "hypothesis_title",
    )

    question = first_available(
        specification,
        "question_description",
        "question_title",
    )

    experiment = first_available(
        specification,
        "experiment_description",
        "experiment_title",
    )

    return {
        "result_id": result_id,
        "artifact_id": metadata.get("artifact_id"),
        "created_at": metadata.get("created_at"),
        "executor_type": metadata.get("executor_type"),
        "data_source": metadata.get("data_source"),
        "parent_artifact_id": lineage.get(
            "parent_artifact_id"
        ),
        "parent_result_id": None,
        "lineage_type": lineage.get("lineage_type"),
        "lineage_change_description": lineage.get(
            "change_description"
        ),
        "created_from_experiment": lineage.get(
            "created_from_experiment"
        ),
        "history": normalize_history(
            artifact.get("history")
        ),
        "question": question,
        "hypothesis": hypothesis,
        "expected_result": specification.get(
            "expected_result"
        ),
        "experiment": experiment,
        "symbol": specification.get("symbol"),
        "timeframe": specification.get("timeframe"),
        "evidence_metrics": evidence_metrics,
        "result_is_valid": first_available(
            evaluation,
            "is_valid",
            "result_is_valid",
        ),
        "evaluation_strength": first_available(
            evaluation,
            "evidence_strength",
            "strength",
        ),
        "evaluation_warnings": as_list(
            evaluation.get("warnings")
        ),
        "statistics_evaluated": first_available(
            statistical_evaluation,
            "is_evaluated",
            "statistics_evaluated",
        ),
        "sample_size": statistical_evaluation.get(
            "sample_size"
        ),
        "statistical_mean": statistical_evaluation.get(
            "mean"
        ),
        "standard_deviation": statistical_evaluation.get(
            "standard_deviation"
        ),
        "standard_error": statistical_evaluation.get(
            "standard_error"
        ),
        "confidence_interval_lower": (
            statistical_evaluation.get(
                "confidence_interval_lower"
            )
        ),
        "confidence_interval_upper": (
            statistical_evaluation.get(
                "confidence_interval_upper"
            )
        ),
        "confidence_level": statistical_evaluation.get(
            "confidence_level"
        ),
        "statistically_significant": first_available(
            statistical_evaluation,
            "is_significant",
            "statistically_significant",
        ),
        "p_value": statistical_evaluation.get(
            "p_value"
        ),
        "effect_size": statistical_evaluation.get(
            "effect_size"
        ),
        "statistical_warnings": as_list(
            statistical_evaluation.get("warnings")
        ),
        "evidence_strength_score": (
            evidence_strength_evaluation.get("score")
        ),
        "evidence_strength_level": (
            evidence_strength_evaluation.get("level")
        ),
        "evidence_strength_evaluated": first_available(
            evidence_strength_evaluation,
            "is_evaluated",
            "evaluated",
        ),
        "evidence_strength_warnings": as_list(
            evidence_strength_evaluation.get(
                "warnings"
            )
        ),
        "hypothesis_decision": first_available(
            hypothesis_decision,
            "decision",
            "status",
            "action",
        ),
        "hypothesis_supported": first_available(
            hypothesis_decision,
            "supported",
            "is_supported",
        ),
        "decision_confidence": hypothesis_decision.get(
            "confidence"
        ),
        "decision_reason": first_available(
            hypothesis_decision,
            "reason",
            "basis",
        ),
        "decision_failed_requirements": as_list(
            hypothesis_decision.get(
                "failed_requirements"
            )
        ),
        "decision_warnings": as_list(
            hypothesis_decision.get("warnings")
        ),
        "conclusion_statement": conclusion.get(
            "statement"
        ),
        "conclusion_supported": conclusion.get(
            "supported"
        ),
        "conclusion_confidence": conclusion.get(
            "confidence"
        ),
        "conclusion_is_provisional": conclusion.get(
            "is_provisional"
        ),
        "conclusion_basis": conclusion.get(
            "basis"
        ),
        "next_experiment_selected": first_available(
            next_experiment_selection,
            "is_selected",
            "selected",
        ),
        "next_experiment_action": (
            next_experiment_selection.get("action")
        ),
        "next_experiment_priority": (
            next_experiment_selection.get("priority")
        ),
        "next_experiment_reason": (
            next_experiment_selection.get("reason")
        ),
        "next_experiment_target_requirement": (
            next_experiment_selection.get(
                "target_requirement"
            )
        ),
        "next_experiment_recommendations": as_list(
            next_experiment_selection.get(
                "recommendations"
            )
        ),
        "next_experiment_warnings": as_list(
            next_experiment_selection.get(
                "warnings"
            )
        ),
    }


def create_app(
    cycle_lister: StoredResearchCycleLister | None = None,
    artifact_getter: StoredResearchArtifactGetter | None = None,
    artifact_comparer: StoredResearchArtifactComparer | None = None,
) -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index() -> str:
        result_ids = (
            cycle_lister.execute()
            if cycle_lister is not None
            else []
        )

        all_artifacts = build_artifact_index(
            result_ids=result_ids,
            artifact_getter=artifact_getter,
        )
        dashboard_statistics = (
            build_dashboard_statistics(
                artifacts=all_artifacts,
            )
        )

        filters = {
            "symbol": request.args.get(
                "symbol",
                "",
            ).strip(),
            "timeframe": request.args.get(
                "timeframe",
                "",
            ).strip(),
            "hypothesis": request.args.get(
                "hypothesis",
                "",
            ).strip(),
            "lineage_type": request.args.get(
                "lineage_type",
                "",
            ).strip(),
        }

        allowed_sort_fields = {
            "created_at",
            "confidence",
            "symbol",
            "lineage_depth",
        }

        sort_by = request.args.get(
            "sort_by",
            "created_at",
        ).strip()

        if sort_by not in allowed_sort_fields:
            sort_by = "created_at"

        sort_direction = request.args.get(
            "sort_direction",
            "descending",
        ).strip()

        if sort_direction not in {
            "ascending",
            "descending",
        }:
            sort_direction = "descending"

        sorting = {
            "sort_by": sort_by,
            "sort_direction": sort_direction,
        }

        artifacts = filter_artifacts(
            artifacts=all_artifacts,
            symbol=filters["symbol"],
            timeframe=filters["timeframe"],
            hypothesis=filters["hypothesis"],
            lineage_type=filters["lineage_type"],
        )

        artifacts = sort_artifacts(
            artifacts=artifacts,
            sort_by=sort_by,
            descending=(
                sort_direction == "descending"
            ),
        )
        try:
            page = int(
                request.args.get(
                    "page",
                    "1",
                )
            )
        except ValueError:
            page = 1

        try:
            page_size = int(
                request.args.get(
                    "page_size",
                    "10",
                )
            )
        except ValueError:
            page_size = 10

        allowed_page_sizes = {
            5,
            10,
            25,
            50,
        }

        if page_size not in allowed_page_sizes:
            page_size = 10

        pagination = paginate_artifacts(
            artifacts=artifacts,
            page=page,
            page_size=page_size,
        )

        paginated_artifacts = pagination[
            "items"
        ]

        filters_are_active = any(
            filters.values()
        )

        (
            lineage_tree,
            orphan_artifacts,
        ) = build_lineage_tree(
            artifacts=artifacts,
        )

        return render_template_string(
            INDEX_TEMPLATE,
            all_artifacts=all_artifacts,
            artifacts=paginated_artifacts,
            dashboard_statistics=(
                dashboard_statistics
            ),
            filtered_artifacts=artifacts,
            pagination=pagination,
            lineage_tree=lineage_tree,
            orphan_artifacts=orphan_artifacts,
            filters=filters,
            sorting=sorting,
            filters_are_active=filters_are_active,
            format_display_value=format_display_value,
        )

    @app.get("/artifacts/<result_id>")
    def artifact_details(
        result_id: str,
    ) -> str:
        if artifact_getter is None:
            abort(404)

        artifact = artifact_getter.execute(
            result_id,
        )

        if artifact is None:
            abort(404)

        details = build_artifact_details(
            result_id=result_id,
            artifact=artifact,
        )

        result_ids = (
            cycle_lister.execute()
            if cycle_lister is not None
            else []
        )

        artifact_index = build_artifact_index(
            result_ids=result_ids,
            artifact_getter=artifact_getter,
        )

        if details["parent_artifact_id"]:
            for indexed_artifact in artifact_index:
                if (
                    indexed_artifact["artifact_id"]
                    == details["parent_artifact_id"]
                ):
                    details["parent_result_id"] = (
                        indexed_artifact["result_id"]
                    )
                    break

        child_artifacts = [
            indexed_artifact
            for indexed_artifact in artifact_index
            if (
                details["artifact_id"]
                and indexed_artifact[
                    "parent_artifact_id"
                ] == details["artifact_id"]
            )
        ]

        return render_template_string(
            ARTIFACT_DETAILS_TEMPLATE,
            details=details,
            child_artifacts=child_artifacts,
            format_display_value=format_display_value,
        )

    @app.get("/compare")
    def compare_artifacts() -> str:
        if artifact_comparer is None:
            abort(404)

        artifact_a_result_id = request.args.get(
            "artifact_a_result_id",
            "",
        ).strip()

        artifact_b_result_id = request.args.get(
            "artifact_b_result_id",
            "",
        ).strip()

        if (
            not artifact_a_result_id
            or not artifact_b_result_id
        ):
            abort(
                400,
                description=(
                    "Both artifact result IDs are required."
                ),
            )

        try:
            comparison = artifact_comparer.execute(
                artifact_a_result_id=artifact_a_result_id,
                artifact_b_result_id=artifact_b_result_id,
            )
        except ValueError as error:
            abort(
                404,
                description=str(error),
            )

        return render_template_string(
            COMPARISON_TEMPLATE,
            comparison=comparison,
            format_display_value=format_display_value,
        )

    return app


def build_web_app(
    db_path: str | Path = RESEARCH_CYCLE_DATABASE_PATH,
) -> Flask:
    store = SqliteResearchCycleStore(
        db_path=db_path,
    )

    cycle_lister = ListStoredResearchCycles(
        store=store,
    )

    artifact_getter = GetStoredResearchArtifact(
        store=store,
    )

    artifact_comparer = CompareStoredResearchArtifacts(
        artifact_getter=artifact_getter,
        input_extractor=ArtifactComparisonInputExtractor(),
    )

    return create_app(
        cycle_lister=cycle_lister,
        artifact_getter=artifact_getter,
        artifact_comparer=artifact_comparer,
    )


def main() -> None:
    app = build_web_app()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
    )


if __name__ == "__main__":
    main()