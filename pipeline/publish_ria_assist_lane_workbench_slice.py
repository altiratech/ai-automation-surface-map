from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKFLOW_PATHS = (
    REPO_ROOT / "artifacts" / "ria_marketing_rule_review.surface_map.json",
    REPO_ROOT / "artifacts" / "ria_annual_adv_update.surface_map.json",
    REPO_ROOT / "artifacts" / "ria_code_of_ethics_exception_review.surface_map.json",
)
DEFAULT_PATTERN_SUMMARY_PATH = REPO_ROOT / "artifacts" / "ria_workflow_pattern_summary.json"
DEFAULT_OUTPUT_PATH = REPO_ROOT / "artifacts" / "ria_assist_lane_workbench_slice.json"
DEFAULT_GENERATED_BY = (
    "/Users/ryanjameson/Desktop/Lifehub/.venv-fastlane/bin/python -m "
    "pipeline.publish_ria_assist_lane_workbench_slice"
)


def _timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _assist_steps(path: Path) -> list[dict]:
    payload = _load_json(path)
    workflow = payload["workflow"]
    assist_steps = []
    for step in payload["step_results"]:
        if step["recommendation"] != "assist":
            continue
        assist_steps.append(
            {
                "workflow_id": workflow["workflow_id"],
                "workflow_name": workflow["workflow_name"],
                "source_artifact_path": str(path.relative_to(REPO_ROOT)),
                **step,
            }
        )
    return assist_steps


def _common_keys(items: list[dict]) -> list[str]:
    if not items:
        return []
    shared = set(items[0].keys())
    for item in items[1:]:
        shared &= set(item.keys())
    return sorted(shared)


def _shared_contract(assist_steps: list[dict]) -> dict:
    sample_artifacts = [artifact for step in assist_steps for artifact in step["artifacts"]]
    sample_evidence = [note for step in assist_steps for note in step["evidence_notes"]]
    sample_reviews = [step["review"] for step in assist_steps]
    return {
        "common_step_fields": _common_keys(assist_steps),
        "common_review_fields": _common_keys(sample_reviews),
        "common_artifact_fields": _common_keys(sample_artifacts),
        "common_evidence_fields": _common_keys(sample_evidence),
    }


def _pilot_steps(assist_steps: list[dict]) -> list[dict]:
    workflow_ids = []
    ordered: list[dict] = []
    for step in assist_steps:
        if step["workflow_id"] not in workflow_ids:
            workflow_ids.append(step["workflow_id"])
    for workflow_id in workflow_ids:
        workflow_steps = [step for step in assist_steps if step["workflow_id"] == workflow_id]
        pilot = max(workflow_steps, key=lambda item: item["build_priority_score"])
        ordered.append(
            {
                "workflow_id": pilot["workflow_id"],
                "workflow_name": pilot["workflow_name"],
                "step_id": pilot["step_id"],
                "step_name": pilot["step_name"],
                "build_priority_score": pilot["build_priority_score"],
                "review_action": pilot["review"]["review_actions"][0] if pilot["review"]["review_actions"] else None,
                "build_implication": pilot["build_implication"],
            }
        )
    return ordered


def _reviewer_confirmation_steps(assist_steps: list[dict]) -> list[dict]:
    flagged = []
    for step in assist_steps:
        for action in step["review"]["review_actions"]:
            if "reviewer confirmation" in action:
                flagged.append(
                    {
                        "workflow_id": step["workflow_id"],
                        "step_id": step["step_id"],
                        "step_name": step["step_name"],
                        "action": action,
                    }
                )
                break
    return flagged


def build_payload(
    *,
    workflow_paths: tuple[Path, ...] = DEFAULT_WORKFLOW_PATHS,
    pattern_summary_path: Path = DEFAULT_PATTERN_SUMMARY_PATH,
) -> dict:
    assist_steps = [step for path in workflow_paths for step in _assist_steps(path)]
    pattern_summary = _load_json(pattern_summary_path)
    pilot_steps = _pilot_steps(assist_steps)

    return {
        "artifact_id": "ria_assist_lane_workbench_slice",
        "artifact_version": "1.0",
        "generated_at": _timestamp(),
        "generated_by": DEFAULT_GENERATED_BY,
        "scope": {
            "workflow_count": len({step["workflow_id"] for step in assist_steps}),
            "assist_step_count": len(assist_steps),
            "pilot_step_count": len(pilot_steps),
            "source_artifacts": [str(path.relative_to(REPO_ROOT)) for path in workflow_paths],
            "pattern_summary_artifact": str(pattern_summary_path.relative_to(REPO_ROOT)),
        },
        "workbench_thesis": {
            "thesis": pattern_summary["product_recommendation"]["thesis"],
            "reason": (
                "The three-slice pattern summary says the next shared build sequence is a reviewer workbench for "
                "assist-lane steps where confirmation, edits, and rationale visibility matter most."
            ),
        },
        "supporting_steps": [
            {
                "workflow_id": step["workflow_id"],
                "workflow_name": step["workflow_name"],
                "step_id": step["step_id"],
                "step_name": step["step_name"],
                "build_priority_score": step["build_priority_score"],
                "review_action": step["review"]["review_actions"][0] if step["review"]["review_actions"] else None,
                "build_implication": step["build_implication"],
            }
            for step in assist_steps
        ],
        "pilot_steps": pilot_steps,
        "shared_contract": _shared_contract(assist_steps),
        "shared_jobs_to_be_done": [
            {
                "job_id": "understand-why-this-step-needs-review",
                "job": "Show why the selected step is in the assist lane, not the automate or keep-human lane.",
                "backed_by_fields": [
                    "mode_scores",
                    "ranked_modes",
                    "confidence",
                    "review.decision_rationale",
                    "review.review_actions",
                ],
            },
            {
                "job_id": "inspect-evidence-and-linked-artifacts",
                "job": "Let the reviewer inspect the evidence notes, supporting artifacts, and score rationales without leaving the step context.",
                "backed_by_fields": [
                    "artifacts",
                    "evidence_notes",
                    "dimension_scores",
                    "build_implication",
                ],
            },
            {
                "job_id": "edit-the-draft-or-rationale",
                "job": "Support reviewer edits to the memo, classification basis, or exception framing before anything moves forward.",
                "backed_by_fields": [
                    "step_description",
                    "review.decision_rationale",
                    "build_implication",
                ],
            },
            {
                "job_id": "record-reviewer-outcome",
                "job": "Capture a visible reviewer outcome such as confirm, revise, or escalate, along with the reason for that choice.",
                "backed_by_fields": [
                    "review.review_actions",
                    "human_owner_role",
                    "hard_human_gate",
                ],
            },
        ],
        "v1_sections": [
            {
                "section_id": "queue",
                "title": "Assist queue",
                "purpose": "Prioritize assist-lane steps across the locked workflows by build priority and reviewer caution.",
                "uses_fields": [
                    "workflow_id",
                    "step_id",
                    "step_name",
                    "build_priority_score",
                    "review.review_actions",
                ],
            },
            {
                "section_id": "context",
                "title": "Selected step context",
                "purpose": "Explain the workflow, owner, step description, and why the product currently recommends assist.",
                "uses_fields": [
                    "workflow_name",
                    "human_owner_role",
                    "step_description",
                    "mode_scores",
                    "review.decision_rationale",
                ],
            },
            {
                "section_id": "evidence",
                "title": "Evidence and artifacts",
                "purpose": "Keep the source-backed evidence, linked artifacts, and score rationales visible while the reviewer works.",
                "uses_fields": [
                    "artifacts",
                    "evidence_notes",
                    "dimension_scores",
                    "review.covered_dimensions",
                ],
            },
            {
                "section_id": "draft",
                "title": "Draft and rationale workspace",
                "purpose": "Give the reviewer one place to edit the classification basis, disclosure call, or memo framing before they decide how to proceed.",
                "uses_fields": [
                    "build_implication",
                    "review.decision_rationale",
                    "review.confidence_breakdown",
                ],
            },
            {
                "section_id": "decision",
                "title": "Reviewer outcome",
                "purpose": "Capture confirm, revise, or escalate outcomes with an explicit reason and prepare a package for the next human gate when needed.",
                "uses_fields": [
                    "review.review_actions",
                    "hard_human_gate",
                    "human_owner_role",
                ],
            },
        ],
        "explicit_non_goals": [
            "Do not collapse the final supervisory step into the workbench; that remains approval support and audit traceability only.",
            "Do not turn this into a workflow router or a multi-workflow dashboard before the assist-lane interaction model is proven.",
            "Do not add autonomous reviewer outcomes in v1; the workbench should prepare and record human judgment, not replace it.",
        ],
        "acceptance_signals": [
            "A reviewer can open any pilot assist step and immediately see why it needs review.",
            "A reviewer can inspect all source-backed evidence and linked artifacts without leaving the selected step.",
            "A reviewer can edit the working rationale or draft output before recording an outcome.",
            "A reviewer can explicitly confirm, revise, or escalate the step with a written reason.",
            "The resulting package can be handed to the final human gate without adding hidden logic."
        ],
        "reviewer_confirmation_pattern": {
            "steps_requiring_explicit_confirmation": _reviewer_confirmation_steps(assist_steps),
            "count": len(_reviewer_confirmation_steps(assist_steps)),
        },
    }


def publish(
    *,
    workflow_paths: tuple[Path, ...] = DEFAULT_WORKFLOW_PATHS,
    pattern_summary_path: Path = DEFAULT_PATTERN_SUMMARY_PATH,
    output_path: Path = DEFAULT_OUTPUT_PATH,
) -> dict:
    payload = build_payload(workflow_paths=workflow_paths, pattern_summary_path=pattern_summary_path)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish the shared assist-lane reviewer-workbench slice artifact.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH, help="Path to the output artifact JSON")
    args = parser.parse_args()
    publish(output_path=args.output)


if __name__ == "__main__":
    main()
