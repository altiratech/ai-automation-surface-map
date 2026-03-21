from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_PATHS = (
    REPO_ROOT / "artifacts" / "ria_marketing_rule_review.surface_map.json",
    REPO_ROOT / "artifacts" / "ria_annual_adv_update.surface_map.json",
    REPO_ROOT / "artifacts" / "ria_code_of_ethics_exception_review.surface_map.json",
)
DEFAULT_OUTPUT_PATH = REPO_ROOT / "artifacts" / "ria_workflow_pattern_summary.json"
DEFAULT_GENERATED_BY = (
    "/Users/ryanjameson/Desktop/Lifehub/.venv-fastlane/bin/python -m "
    "pipeline.publish_ria_workflow_pattern_summary"
)


def _timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_payload(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _workflow_snapshot(path: Path, payload: dict) -> dict:
    return {
        "workflow_id": payload["workflow"]["workflow_id"],
        "workflow_name": payload["workflow"]["workflow_name"],
        "artifact_path": str(path.relative_to(REPO_ROOT)),
        "workflow_trust_score": payload["trust_summary"]["workflow_trust_score"],
        "mode_counts": payload["summary"]["mode_counts"],
        "highest_priority_build_step": payload["summary"]["highest_priority_build_step"],
        "hard_guardrail_step": payload["summary"]["hard_guardrail_step"],
        "weakest_step": payload["trust_summary"]["weakest_step"],
        "review_queue": payload["trust_summary"]["review_queue"],
    }


def _review_queue_pattern(workflow_snapshots: list[dict]) -> dict:
    reviewer_confirmation_steps: list[dict] = []
    approval_support_steps: list[dict] = []

    for snapshot in workflow_snapshots:
        for queue_item in snapshot["review_queue"]:
            if "reviewer confirmation" in queue_item["action"]:
                reviewer_confirmation_steps.append(
                    {
                        "workflow_id": snapshot["workflow_id"],
                        "step_id": queue_item["step_id"],
                        "action": queue_item["action"],
                    }
                )
            if "approval support and audit traceability" in queue_item["action"]:
                approval_support_steps.append(
                    {
                        "workflow_id": snapshot["workflow_id"],
                        "step_id": queue_item["step_id"],
                        "action": queue_item["action"],
                    }
                )

    return {
        "reviewer_confirmation_steps": reviewer_confirmation_steps,
        "approval_support_steps": approval_support_steps,
    }


def _product_patterns(workflow_snapshots: list[dict]) -> list[dict]:
    return [
        {
            "pattern_id": "automate-buildable-edge-first",
            "finding": "Across all three locked workflows, the first build wedge is still a buildable automate step rather than a final reviewer action.",
            "support": [
                {
                    "workflow_id": snapshot["workflow_id"],
                    "step_id": snapshot["highest_priority_build_step"]["step_id"],
                    "step_name": snapshot["highest_priority_build_step"]["step_name"],
                    "recommendation": snapshot["highest_priority_build_step"]["recommendation"],
                    "build_priority_score": snapshot["highest_priority_build_step"]["build_priority_score"],
                }
                for snapshot in workflow_snapshots
            ],
            "product_implication": "Build the product around evidence assembly, exception detection, and structured drafting before adding more reviewer-facing surface area.",
        },
        {
            "pattern_id": "assist-lane-carries-the-main-caution",
            "finding": "The recurring caution across workflows sits in the assist lane: judgment-dense middle steps still need strong reviewer confirmation.",
            "support": [
                {
                    "workflow_id": snapshot["workflow_id"],
                    "step_id": queue_item["step_id"],
                    "action": queue_item["action"],
                }
                for snapshot in workflow_snapshots
                for queue_item in snapshot["review_queue"]
                if "reviewer confirmation" in queue_item["action"]
            ],
            "product_implication": "The next shared product layer should help reviewers inspect and edit exception calls, not auto-resolve those middle-step judgments.",
        },
        {
            "pattern_id": "final-accountable-step-stays-human",
            "finding": "Each workflow ends with an explicit keep-human supervisory gate even when the rest of the workflow is highly structureable.",
            "support": [
                {
                    "workflow_id": snapshot["workflow_id"],
                    "step_id": snapshot["hard_guardrail_step"]["step_id"],
                    "step_name": snapshot["hard_guardrail_step"]["step_name"],
                    "recommendation": snapshot["hard_guardrail_step"]["recommendation"],
                    "build_priority_score": snapshot["hard_guardrail_step"]["build_priority_score"],
                }
                for snapshot in workflow_snapshots
            ],
            "product_implication": "Do not build end-to-end autonomous approval, filing, or violation adjudication. Keep the final decision as approval support and audit traceability only.",
        },
    ]


def build_payload(*, input_paths: tuple[Path, ...] = DEFAULT_INPUT_PATHS) -> dict:
    artifacts = [(_load_payload(path), path) for path in input_paths]
    workflow_snapshots = [_workflow_snapshot(path, payload) for payload, path in artifacts]
    mode_shapes = [snapshot["mode_counts"] for snapshot in workflow_snapshots]
    common_mode_shape = mode_shapes[0]
    shared_by_all = all(mode_shape == common_mode_shape for mode_shape in mode_shapes)
    average_workflow_trust_score = round(mean(snapshot["workflow_trust_score"] for snapshot in workflow_snapshots))
    highest_priority_steps_are_buildable = all(
        snapshot["highest_priority_build_step"]["recommendation"] == "automate"
        for snapshot in workflow_snapshots
    )
    hard_guardrails_are_human = all(
        snapshot["hard_guardrail_step"]["recommendation"] == "keep-human"
        for snapshot in workflow_snapshots
    )

    return {
        "artifact_id": "ria_workflow_pattern_summary",
        "artifact_version": "1.0",
        "generated_at": _timestamp(),
        "generated_by": DEFAULT_GENERATED_BY,
        "portfolio_scope": {
            "workflow_count": len(workflow_snapshots),
            "workflow_ids": [snapshot["workflow_id"] for snapshot in workflow_snapshots],
            "note": "This is a static synthesis of the three locked RIA workflow slices currently committed in the repo.",
        },
        "workflow_snapshots": workflow_snapshots,
        "cross_workflow_observations": {
            "common_mode_shape": {
                "mode_counts": common_mode_shape,
                "shared_by_all": shared_by_all,
            },
            "average_workflow_trust_score": average_workflow_trust_score,
            "highest_priority_steps_are_buildable": highest_priority_steps_are_buildable,
            "hard_guardrails_are_human": hard_guardrails_are_human,
            "review_queue_pattern": _review_queue_pattern(workflow_snapshots),
        },
        "product_patterns": _product_patterns(workflow_snapshots),
        "product_recommendation": {
            "thesis": "The product is shaping into a compliance evidence and exception-preparation engine, not an autonomous compliance operator.",
            "next_build_sequence": [
                "Standardize evidence assembly, exception detection, and structured drafting across locked workflows before adding more UI.",
                "Build a reviewer workbench for assist-lane steps where confirmation, edits, and rationale visibility matter most.",
                "Keep the final supervisory step limited to approval support and audit traceability rather than autonomous action."
            ],
            "explicit_non_goals": [
                "Do not build end-to-end autonomous approval, filing, or sanctions decisions.",
                "Do not widen the UI just to browse more workflows before the shared reviewer pattern is clearer.",
                "Do not turn the repo into general workflow routing or orchestration yet."
            ],
        },
    }


def publish(
    *,
    input_paths: tuple[Path, ...] = DEFAULT_INPUT_PATHS,
    output_path: Path = DEFAULT_OUTPUT_PATH,
) -> dict:
    payload = build_payload(input_paths=input_paths)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish the three-slice RIA workflow pattern summary artifact.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH, help="Path to the output artifact JSON")
    args = parser.parse_args()
    publish(output_path=args.output)


if __name__ == "__main__":
    main()
