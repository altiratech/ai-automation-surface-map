from __future__ import annotations

from dataclasses import dataclass

from .models import ScoringConfig, WorkflowBundle
from .scoring import KEEP_HUMAN, ScoredStep


@dataclass(frozen=True)
class StepTrustReview:
    step_id: str
    trust_score: int
    trust_grade: str
    source_count: int
    evidence_note_count: int
    artifact_count: int
    covered_dimensions: tuple[str, ...]
    missing_dimensions: tuple[str, ...]
    unknown_count: int
    read_only_ui_ready: bool
    confidence_breakdown: dict[str, float | int | str]
    decision_rationale: dict[str, str]
    review_actions: tuple[str, ...]


@dataclass(frozen=True)
class WorkflowTrustSummary:
    workflow_trust_score: int
    workflow_trust_grade: str
    read_only_ui_ready: bool
    weakest_step_id: str
    weakest_step_score: int
    review_queue: tuple[dict[str, str], ...]
    blocking_items: tuple[str, ...]


def _grade(score: int) -> str:
    if score >= 85:
        return "A"
    if score >= 75:
        return "B"
    if score >= 65:
        return "C"
    return "D"


def _confidence_note(scored_step: ScoredStep) -> str:
    if scored_step.top_mode_margin <= 5:
        return "Low separation between the top two modes means this step still needs explicit reviewer judgment."
    if scored_step.top_mode_margin <= 10:
        return "Moderate score separation supports the recommendation, but the second-best mode remains plausible."
    return "Clear score separation supports the current recommendation."


def _decision_rationale(scored_step: ScoredStep) -> dict[str, str]:
    step = scored_step.step
    automation_fit = step.dimension_value("automation_fit")
    human_signoff = step.dimension_value("human_signoff_need")
    liability = step.dimension_value("liability_asymmetry")
    evidence = step.dimension_value("evidence_strength")

    if scored_step.recommendation == "automate":
        return {
            "why_this_mode": (
                f"Automate is the best fit because automation fit ({automation_fit}) and evidence strength ({evidence}) "
                f"comfortably outweigh human sign-off need ({human_signoff}) and liability asymmetry ({liability})."
            ),
            "why_not_more_human": "Human review should stay focused on exceptions, not default packet handling.",
            "confidence_note": _confidence_note(scored_step),
        }
    if scored_step.recommendation == "assist":
        return {
            "why_this_mode": (
                f"Assist is the right lane because the step is partially structured ({automation_fit}) but still carries "
                f"meaningful human sign-off need ({human_signoff}) and liability asymmetry ({liability})."
            ),
            "why_not_automate": "Do not let this step resolve the review on its own; it should prepare judgment, not replace it.",
            "confidence_note": _confidence_note(scored_step),
        }
    if scored_step.gating_reason == "hard-human-gate":
        why_keep_human = "Keep Human is mandatory because this step is an explicit supervisory approval point."
    else:
        why_keep_human = (
            f"Keep Human is the safest fit because human sign-off need ({human_signoff}) and liability asymmetry ({liability}) "
            f"are both too high for autonomous handling."
        )
    return {
        "why_this_mode": why_keep_human,
        "why_not_automate": "Automation here should only package context and evidence for the accountable reviewer.",
        "confidence_note": _confidence_note(scored_step),
    }


def _review_actions(scored_step: ScoredStep, missing_dimensions: tuple[str, ...], config: ScoringConfig) -> tuple[str, ...]:
    actions: list[str] = []
    step = scored_step.step
    min_sources = config.review_thresholds["min_source_count_per_step"]

    if len(step.source_ids) < min_sources:
        actions.append(f"Add at least {min_sources - len(step.source_ids)} more official source anchor(s) for this step.")
    if missing_dimensions:
        joined = ", ".join(missing_dimensions)
        actions.append(f"Add explicit evidence coverage for these score dimensions: {joined}.")
    if scored_step.confidence < 0.45:
        actions.append("Tighten the rationale or add supporting evidence because the score spread is still narrow.")
    if step.unknowns:
        actions.append("Resolve the listed unknowns before turning this step into stronger product logic.")
    if scored_step.recommendation == KEEP_HUMAN:
        actions.append("Keep any future UI limited to approval support and audit traceability, not autonomous action.")
    elif scored_step.recommendation == "assist" and step.dimension_value("liability_asymmetry") >= 70:
        actions.append("Keep reviewer confirmation prominent because the downside of a bad recommendation is still high.")

    return tuple(dict.fromkeys(actions))


def review_step(scored_step: ScoredStep, bundle: WorkflowBundle, config: ScoringConfig) -> StepTrustReview:
    step = scored_step.step
    supported_dimensions = tuple(sorted(step.supported_dimensions()))
    unknown_dimension_tags = sorted(set(supported_dimensions) - set(config.dimensions))
    if unknown_dimension_tags:
        joined = ", ".join(unknown_dimension_tags)
        raise ValueError(f"{step.step_id} references unknown dimensions in evidence notes: {joined}")
    missing_dimensions = tuple(sorted(set(config.dimensions) - set(supported_dimensions)))

    dimension_coverage_pct = round((len(supported_dimensions) / len(config.dimensions)) * 100)
    source_count = len(step.source_ids)
    evidence_note_count = len(step.evidence_notes)
    artifact_count = len(step.artifact_ids)
    min_sources = config.review_thresholds["min_source_count_per_step"]
    source_count_score = min(100, round((source_count / min_sources) * 100))
    evidence_density_score = min(100, round((evidence_note_count / len(config.dimensions)) * 100))
    unknown_penalty = min(30, len(step.unknowns) * 10)

    trust_score = round(
        (scored_step.confidence * 100 * 0.35)
        + (dimension_coverage_pct * 0.30)
        + (source_count_score * 0.15)
        + (evidence_density_score * 0.10)
        + ((100 - unknown_penalty) * 0.10)
    )
    read_only_ui_ready = (
        trust_score >= config.review_thresholds["min_step_trust_score_for_read_only_ui"]
        and dimension_coverage_pct >= config.review_thresholds["min_dimension_coverage_pct"]
        and source_count >= min_sources
    )

    return StepTrustReview(
        step_id=step.step_id,
        trust_score=trust_score,
        trust_grade=_grade(trust_score),
        source_count=source_count,
        evidence_note_count=evidence_note_count,
        artifact_count=artifact_count,
        covered_dimensions=supported_dimensions,
        missing_dimensions=missing_dimensions,
        unknown_count=len(step.unknowns),
        read_only_ui_ready=read_only_ui_ready,
        confidence_breakdown={
            "confidence": scored_step.confidence,
            "top_mode_margin": scored_step.top_mode_margin,
            "evidence_strength": step.dimension_value("evidence_strength"),
            "note": _confidence_note(scored_step),
        },
        decision_rationale=_decision_rationale(scored_step),
        review_actions=_review_actions(scored_step, missing_dimensions, config),
    )


def review_workflow(
    scored_steps: list[ScoredStep],
    bundle: WorkflowBundle,
    config: ScoringConfig,
) -> tuple[dict[str, StepTrustReview], WorkflowTrustSummary]:
    step_reviews = {
        scored_step.step.step_id: review_step(scored_step, bundle, config)
        for scored_step in scored_steps
    }
    workflow_trust_score = round(sum(review.trust_score for review in step_reviews.values()) / len(step_reviews))
    weakest_step = min(step_reviews.values(), key=lambda review: review.trust_score)
    blocking_items: list[str] = []
    if weakest_step.trust_score < config.review_thresholds["min_step_trust_score_for_read_only_ui"]:
        blocking_items.append("At least one step still falls below the minimum trust score for a read-only UI.")
    if any(review.missing_dimensions for review in step_reviews.values()):
        blocking_items.append("Some step-level score dimensions still lack explicit source-backed evidence coverage.")
    if any(review.source_count < config.review_thresholds["min_source_count_per_step"] for review in step_reviews.values()):
        blocking_items.append("Some steps still rely on fewer official sources than the trust pass requires.")

    read_only_ui_ready = (
        workflow_trust_score >= config.review_thresholds["min_workflow_trust_score_for_read_only_ui"]
        and not blocking_items
    )
    actionable_reviews = [
        review for review in sorted(step_reviews.values(), key=lambda item: item.trust_score) if review.review_actions
    ]
    review_queue_source = actionable_reviews or sorted(step_reviews.values(), key=lambda item: item.trust_score)
    review_queue = tuple(
        {
            "step_id": review.step_id,
            "priority": "high" if review.trust_score == weakest_step.trust_score else "medium",
            "action": review.review_actions[0] if review.review_actions else "No immediate action required.",
        }
        for review in review_queue_source[:3]
    )

    summary = WorkflowTrustSummary(
        workflow_trust_score=workflow_trust_score,
        workflow_trust_grade=_grade(workflow_trust_score),
        read_only_ui_ready=read_only_ui_ready,
        weakest_step_id=weakest_step.step_id,
        weakest_step_score=weakest_step.trust_score,
        review_queue=review_queue,
        blocking_items=tuple(blocking_items),
    )
    return step_reviews, summary
