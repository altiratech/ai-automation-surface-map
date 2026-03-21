from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from .io import load_scoring_config, load_workflow_bundle
from .review import review_workflow
from .scoring import KEEP_HUMAN, score_workflow


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = REPO_ROOT / "configs" / "ria_marketing_rule_review.scoring.json"
DEFAULT_WORKFLOW_PATH = REPO_ROOT / "data" / "ria_marketing_rule_review.workflow.json"
DEFAULT_OUTPUT_PATH = REPO_ROOT / "artifacts" / "ria_marketing_rule_review.surface_map.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _serialize_sources(bundle) -> list[dict]:
    return [
        {
            "source_id": source.source_id,
            "title": source.title,
            "source_type": source.source_type,
            "publisher": source.publisher,
            "published_date": source.published_date,
            "url": source.url,
            "summary": source.summary,
        }
        for source in sorted(bundle.sources.values(), key=lambda item: item.source_id)
    ]


def _serialize_artifacts(bundle) -> list[dict]:
    return [
        {
            "artifact_id": artifact.artifact_id,
            "name": artifact.name,
            "artifact_type": artifact.artifact_type,
            "origin": artifact.origin,
            "description": artifact.description,
            "step_ids": list(artifact.step_ids),
        }
        for artifact in sorted(bundle.artifacts.values(), key=lambda item: item.artifact_id)
    ]


def _serialize_step_result(scored_step, review, bundle, config) -> dict:
    step = scored_step.step
    return {
        "step_id": step.step_id,
        "step_order": step.step_order,
        "step_name": step.step_name,
        "step_description": step.step_description,
        "human_owner_role": step.human_owner_role,
        "recommendation": scored_step.recommendation,
        "mode_scores": scored_step.mode_scores,
        "ranked_modes": list(scored_step.ranked_modes),
        "build_priority_score": scored_step.build_priority_score,
        "confidence": scored_step.confidence,
        "hard_human_gate": step.hard_human_gate,
        "gating_reason": scored_step.gating_reason,
        "artifacts": [
            {
                "artifact_id": artifact_id,
                "name": bundle.artifacts[artifact_id].name,
                "artifact_type": bundle.artifacts[artifact_id].artifact_type,
            }
            for artifact_id in step.artifact_ids
        ],
        "dimension_scores": {
            key: {
                "label": config.dimensions[key].label,
                "value": assessment.value,
                "rationale": assessment.rationale,
            }
            for key, assessment in step.dimension_scores.items()
        },
        "evidence_notes": [
            {
                "source_id": note.source_id,
                "source_title": bundle.sources[note.source_id].title,
                "source_url": bundle.sources[note.source_id].url,
                "claim": note.claim,
                "supports_dimensions": list(note.supports_dimensions),
            }
            for note in step.evidence_notes
        ],
        "unknowns": list(step.unknowns),
        "build_implication": step.build_implication,
        "review": {
            "trust_score": review.trust_score,
            "trust_grade": review.trust_grade,
            "source_count": review.source_count,
            "evidence_note_count": review.evidence_note_count,
            "artifact_count": review.artifact_count,
            "covered_dimensions": list(review.covered_dimensions),
            "missing_dimensions": list(review.missing_dimensions),
            "unknown_count": review.unknown_count,
            "read_only_ui_ready": review.read_only_ui_ready,
            "confidence_breakdown": review.confidence_breakdown,
            "decision_rationale": review.decision_rationale,
            "review_actions": list(review.review_actions),
        },
    }


def _build_decisions(scored_steps) -> list[dict]:
    automate_steps = sorted(
        (item for item in scored_steps if item.recommendation == "automate"),
        key=lambda item: item.build_priority_score,
        reverse=True,
    )
    assist_steps = sorted(
        (item for item in scored_steps if item.recommendation == "assist"),
        key=lambda item: item.build_priority_score,
        reverse=True,
    )
    keep_human_steps = sorted(
        (item for item in scored_steps if item.recommendation == KEEP_HUMAN),
        key=lambda item: item.build_priority_score,
        reverse=True,
    )

    decisions: list[dict] = []
    if automate_steps:
        decisions.append(
            {
                "decision_type": "prioritize-automation",
                "decision": "Build automation around intake, substantiation assembly, and archival packaging before any reviewer-facing UI.",
                "step_ids": [step.step.step_id for step in automate_steps],
                "rationale": "These steps scored high on automation fit and evidence strength while staying below the configured liability and sign-off gates.",
            }
        )
    if assist_steps:
        decisions.append(
            {
                "decision_type": "prioritize-assist",
                "decision": "Build human-in-the-loop review aids for classification, content-flagging, and remediation drafting instead of autonomous adjudication.",
                "step_ids": [step.step.step_id for step in assist_steps],
                "rationale": "These steps benefit from structured guidance, but they still carry meaningful judgment and liability that should stay visible to a reviewer.",
            }
        )
    if keep_human_steps:
        decisions.append(
            {
                "decision_type": "enforce-human-gate",
                "decision": "Do not build end-to-end autonomous approval or publication in slice 1.",
                "step_ids": [step.step.step_id for step in keep_human_steps],
                "rationale": "The publication-approval step remains a named human responsibility with asymmetric downside if a bad ad is cleared.",
            }
        )
    return decisions


def build_payload(
    *,
    config_path: Path = DEFAULT_CONFIG_PATH,
    workflow_path: Path = DEFAULT_WORKFLOW_PATH,
) -> dict:
    config = load_scoring_config(config_path)
    bundle = load_workflow_bundle(workflow_path)
    if bundle.workflow.workflow_id != config.workflow_id:
        raise ValueError(
            f"Workflow id mismatch: config expects {config.workflow_id}, bundle contains {bundle.workflow.workflow_id}"
        )

    scored_steps = score_workflow(bundle.steps, config)
    step_reviews, workflow_review = review_workflow(scored_steps, bundle, config)
    step_results = [
        _serialize_step_result(step_result, step_reviews[step_result.step.step_id], bundle, config)
        for step_result in scored_steps
    ]

    mode_counts = {
        "automate": sum(1 for step in scored_steps if step.recommendation == "automate"),
        "assist": sum(1 for step in scored_steps if step.recommendation == "assist"),
        KEEP_HUMAN: sum(1 for step in scored_steps if step.recommendation == KEEP_HUMAN),
    }
    buildable_steps = [step for step in scored_steps if step.recommendation != KEEP_HUMAN]
    highest_priority_build_step = max(buildable_steps, key=lambda item: item.build_priority_score)
    hard_guardrail_step = max(
        (step for step in scored_steps if step.recommendation == KEEP_HUMAN),
        key=lambda item: item.build_priority_score,
    )
    lowest_confidence = min(scored_steps, key=lambda item: item.confidence)

    return {
        "artifact_id": "ria_marketing_rule_review_surface_map",
        "artifact_version": "1.0",
        "generated_at": _timestamp(),
        "generated_by": "/Users/ryanjameson/Desktop/Lifehub/.venv-fastlane/bin/python -m pipeline.publish",
        "workflow": {
            "workflow_id": bundle.workflow.workflow_id,
            "workflow_name": bundle.workflow.workflow_name,
            "domain": bundle.workflow.domain,
            "persona": bundle.workflow.persona,
            "entry_condition": bundle.workflow.entry_condition,
            "completion_condition": bundle.workflow.completion_condition,
            "workflow_notes": list(bundle.workflow.workflow_notes),
        },
        "observed_inputs": {
            "source_count": len(bundle.sources),
            "artifact_count": len(bundle.artifacts),
            "step_count": len(bundle.steps),
            "note": "Source and artifact inventories are observed or curated workflow inputs. Scores and recommendations are inferred from those inputs."
        },
        "scoring_config": {
            "config_id": config.config_id,
            "version": config.version,
            "dimensions": [
                {
                    "key": dimension.key,
                    "label": dimension.label,
                    "description": dimension.description,
                }
                for dimension in config.dimensions.values()
            ],
            "gates": config.gates,
            "review_thresholds": config.review_thresholds,
        },
        "source_inventory": _serialize_sources(bundle),
        "artifact_inventory": _serialize_artifacts(bundle),
        "summary": {
            "mode_counts": mode_counts,
            "first_build_wedge": "Automate the workflow edges, assist the judgment-heavy middle, and keep final publication approval human.",
            "highest_priority_build_step": {
                "step_id": highest_priority_build_step.step.step_id,
                "step_name": highest_priority_build_step.step.step_name,
                "recommendation": highest_priority_build_step.recommendation,
                "build_priority_score": highest_priority_build_step.build_priority_score,
            },
            "hard_guardrail_step": {
                "step_id": hard_guardrail_step.step.step_id,
                "step_name": hard_guardrail_step.step.step_name,
                "recommendation": hard_guardrail_step.recommendation,
                "build_priority_score": hard_guardrail_step.build_priority_score,
            },
            "lowest_confidence_step": {
                "step_id": lowest_confidence.step.step_id,
                "step_name": lowest_confidence.step.step_name,
                "confidence": lowest_confidence.confidence,
            },
            "blocked_pattern": "Do not ship autonomous end-to-end approval or publication for this workflow in slice 1."
        },
        "trust_summary": {
            "workflow_trust_score": workflow_review.workflow_trust_score,
            "workflow_trust_grade": workflow_review.workflow_trust_grade,
            "read_only_ui_ready": workflow_review.read_only_ui_ready,
            "weakest_step": {
                "step_id": workflow_review.weakest_step_id,
                "trust_score": workflow_review.weakest_step_score,
            },
            "review_queue": list(workflow_review.review_queue),
            "blocking_items": list(workflow_review.blocking_items),
        },
        "step_results": step_results,
        "build_decisions": _build_decisions(scored_steps),
        "explicit_defers": [
            "No orchestration layer",
            "No multi-workflow comparison",
            "No deployment surface",
            "No reviewer UI beyond this published payload"
        ],
    }


def publish(
    *,
    config_path: Path = DEFAULT_CONFIG_PATH,
    workflow_path: Path = DEFAULT_WORKFLOW_PATH,
    output_path: Path = DEFAULT_OUTPUT_PATH,
) -> dict:
    payload = build_payload(config_path=config_path, workflow_path=workflow_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish the first workflow surface-map artifact.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH, help="Path to the scoring config JSON")
    parser.add_argument("--workflow", type=Path, default=DEFAULT_WORKFLOW_PATH, help="Path to the workflow JSON")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH, help="Path to the output artifact JSON")
    args = parser.parse_args()
    publish(config_path=args.config, workflow_path=args.workflow, output_path=args.output)


if __name__ == "__main__":
    main()
