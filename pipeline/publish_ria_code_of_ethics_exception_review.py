from __future__ import annotations

import argparse
from pathlib import Path

from .publish import (
    REPO_ROOT,
    DecisionTemplate,
    WorkflowPublishProfile,
    build_payload as base_build_payload,
    publish as base_publish,
)


DEFAULT_CONFIG_PATH = REPO_ROOT / "configs" / "ria_code_of_ethics_exception_review.scoring.json"
DEFAULT_WORKFLOW_PATH = REPO_ROOT / "data" / "ria_code_of_ethics_exception_review.workflow.json"
DEFAULT_OUTPUT_PATH = REPO_ROOT / "artifacts" / "ria_code_of_ethics_exception_review.surface_map.json"
DEFAULT_GENERATED_BY = (
    "/Users/ryanjameson/Desktop/Lifehub/.venv-fastlane/bin/python -m "
    "pipeline.publish_ria_code_of_ethics_exception_review"
)
DEFAULT_PUBLISH_PROFILE = WorkflowPublishProfile(
    artifact_id="ria_code_of_ethics_exception_review_surface_map",
    first_build_wedge=(
        "Automate the monitoring rails, assist the conflict-heavy exception review, and keep final violation "
        "adjudication human."
    ),
    blocked_pattern=(
        "Do not ship autonomous violation adjudication, sanctions assignment, or waiver approval for this "
        "workflow in slice 3."
    ),
    decision_templates={
        "automate": DecisionTemplate(
            decision_type="prioritize-automation",
            decision=(
                "Build automation around packet assembly, missing-report detection, and post-decision retention "
                "before expanding reviewer UI."
            ),
            rationale=(
                "These steps are repeated monitoring mechanics with strong rule and exam anchors, and they create "
                "clean inputs for a reviewer without deciding whether conduct was a violation."
            ),
        ),
        "assist": DecisionTemplate(
            decision_type="prioritize-assist",
            decision=(
                "Build reviewer aids for access-person scope checks, restricted-list and preclearance review, "
                "and remediation drafting instead of auto-calling violations."
            ),
            rationale=(
                "These steps combine structured checks with conflict and supervisory judgment that should stay "
                "visible to a compliance reviewer."
            ),
        ),
        "keep-human": DecisionTemplate(
            decision_type="enforce-human-gate",
            decision="Do not automate final code-of-ethics violation, waiver, or sanctions decisions in slice 3.",
            rationale=(
                "The adjudication step is an accountable supervisory decision with disciplinary, disclosure, and "
                "books-and-records consequences, so automation should only package evidence for the CCO."
            ),
        ),
    },
)


def build_payload(
    *,
    config_path: Path = DEFAULT_CONFIG_PATH,
    workflow_path: Path = DEFAULT_WORKFLOW_PATH,
) -> dict:
    return base_build_payload(
        config_path=config_path,
        workflow_path=workflow_path,
        generated_by=DEFAULT_GENERATED_BY,
        publish_profile=DEFAULT_PUBLISH_PROFILE,
    )


def publish(
    *,
    config_path: Path = DEFAULT_CONFIG_PATH,
    workflow_path: Path = DEFAULT_WORKFLOW_PATH,
    output_path: Path = DEFAULT_OUTPUT_PATH,
) -> dict:
    return base_publish(
        config_path=config_path,
        workflow_path=workflow_path,
        output_path=output_path,
        generated_by=DEFAULT_GENERATED_BY,
        publish_profile=DEFAULT_PUBLISH_PROFILE,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish the third locked workflow surface-map artifact.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH, help="Path to the scoring config JSON")
    parser.add_argument("--workflow", type=Path, default=DEFAULT_WORKFLOW_PATH, help="Path to the workflow JSON")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH, help="Path to the output artifact JSON")
    args = parser.parse_args()
    publish(config_path=args.config, workflow_path=args.workflow, output_path=args.output)


if __name__ == "__main__":
    main()
