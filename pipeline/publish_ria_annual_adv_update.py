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


DEFAULT_CONFIG_PATH = REPO_ROOT / "configs" / "ria_annual_adv_update.scoring.json"
DEFAULT_WORKFLOW_PATH = REPO_ROOT / "data" / "ria_annual_adv_update.workflow.json"
DEFAULT_OUTPUT_PATH = REPO_ROOT / "artifacts" / "ria_annual_adv_update.surface_map.json"
DEFAULT_GENERATED_BY = (
    "/Users/ryanjameson/Desktop/Lifehub/.venv-fastlane/bin/python -m pipeline.publish_ria_annual_adv_update"
)
DEFAULT_PUBLISH_PROFILE = WorkflowPublishProfile(
    artifact_id="ria_annual_adv_update_surface_map",
    first_build_wedge=(
        "Automate the annual filing mechanics, assist the disclosure-heavy reconciliation work, and keep final "
        "filing execution human."
    ),
    blocked_pattern="Do not ship autonomous annual amendment certification or IARD submission for this workflow in slice 2.",
    decision_templates={
        "automate": DecisionTemplate(
            decision_type="prioritize-automation",
            decision=(
                "Build automation around packet assembly, structured field drafting, notice-filing prep, and "
                "post-filing archival before expanding reviewer UI."
            ),
            rationale=(
                "These steps are repeated, rules-based filing mechanics with strong instruction-level anchors and "
                "lower downside when a human still reviews the final packet."
            ),
        ),
        "assist": DecisionTemplate(
            decision_type="prioritize-assist",
            decision=(
                "Build reviewer aids for registration-basis checks, brochure/material-change reconciliation, and "
                "readiness memo preparation instead of autonomous filing judgment."
            ),
            rationale=(
                "These steps combine structured data with disclosure and eligibility judgment that should stay "
                "visible to a compliance reviewer."
            ),
        ),
        "keep-human": DecisionTemplate(
            decision_type="enforce-human-gate",
            decision="Do not automate final certification or IARD submission in slice 2.",
            rationale=(
                "The execution step is a regulatory filing with public-disclosure and misstatement consequences, "
                "so automation should only stage evidence for the accountable signer."
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
    parser = argparse.ArgumentParser(description="Publish the second locked workflow surface-map artifact.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH, help="Path to the scoring config JSON")
    parser.add_argument("--workflow", type=Path, default=DEFAULT_WORKFLOW_PATH, help="Path to the workflow JSON")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH, help="Path to the output artifact JSON")
    args = parser.parse_args()
    publish(config_path=args.config, workflow_path=args.workflow, output_path=args.output)


if __name__ == "__main__":
    main()
