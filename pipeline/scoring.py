from __future__ import annotations

from dataclasses import dataclass

from .models import ScoringConfig, WorkflowStep


KEEP_HUMAN = "keep-human"


@dataclass(frozen=True)
class ScoredStep:
    step: WorkflowStep
    mode_scores: dict[str, int]
    ranked_modes: tuple[str, ...]
    recommendation: str
    confidence: float
    top_mode_margin: int
    gating_reason: str | None
    build_priority_score: int


def _score_mode(step: WorkflowStep, config: ScoringConfig, mode: str) -> int:
    formula = config.mode_formulas[mode]
    total = 0.0
    for dimension_key, term in formula.terms.items():
        value = step.dimension_value(dimension_key)
        effective_value = value if term.direction == "direct" else 100 - value
        total += effective_value * term.weight
    return round(total)


def _choose_recommendation(step: WorkflowStep, mode_scores: dict[str, int], config: ScoringConfig) -> tuple[str, str | None]:
    human_signoff = step.dimension_value("human_signoff_need")
    liability = step.dimension_value("liability_asymmetry")
    evidence = step.dimension_value("evidence_strength")

    if step.hard_human_gate:
        return KEEP_HUMAN, "hard-human-gate"
    if (
        human_signoff >= config.gates["keep_human_min_human_signoff"]
        and liability >= config.gates["keep_human_min_liability"]
    ):
        return KEEP_HUMAN, "high-liability-high-signoff"

    ranked_modes = sorted(mode_scores, key=mode_scores.get, reverse=True)
    top_mode = ranked_modes[0]
    if top_mode == "automate":
        if (
            human_signoff <= config.gates["automate_max_human_signoff"]
            and liability <= config.gates["automate_max_liability"]
            and evidence >= config.gates["automate_min_evidence"]
        ):
            return "automate", None
        return "assist", "automation-gated-to-assist"
    if top_mode == KEEP_HUMAN:
        return KEEP_HUMAN, None
    return "assist", None


def _confidence(mode_scores: dict[str, int], evidence_strength: int) -> float:
    ordered = sorted(mode_scores.values(), reverse=True)
    margin = ordered[0] - ordered[1]
    score = ((evidence_strength / 100.0) * 0.55) + ((margin / 100.0) * 0.45)
    bounded = max(0.35, min(0.95, score))
    return round(bounded, 2)


def _top_mode_margin(mode_scores: dict[str, int]) -> int:
    ordered = sorted(mode_scores.values(), reverse=True)
    return ordered[0] - ordered[1]


def _build_priority_score(step: WorkflowStep, recommendation: str, mode_scores: dict[str, int]) -> int:
    automation_fit = step.dimension_value("automation_fit")
    human_signoff = step.dimension_value("human_signoff_need")
    liability = step.dimension_value("liability_asymmetry")
    evidence = step.dimension_value("evidence_strength")

    if recommendation == "automate":
        return round((mode_scores["automate"] * 0.60) + (automation_fit * 0.25) + (evidence * 0.15))
    if recommendation == "assist":
        return round(
            (mode_scores["assist"] * 0.55)
            + (automation_fit * 0.20)
            + (evidence * 0.15)
            + (human_signoff * 0.10)
        )
    return round((mode_scores[KEEP_HUMAN] * 0.50) + (human_signoff * 0.25) + (liability * 0.25))


def score_workflow(steps: tuple[WorkflowStep, ...], config: ScoringConfig) -> list[ScoredStep]:
    scored_steps: list[ScoredStep] = []
    required_dimensions = set(config.dimensions)

    for step in steps:
        step_dimensions = set(step.dimension_scores)
        missing = required_dimensions - step_dimensions
        extra = step_dimensions - required_dimensions
        if missing:
            joined = ", ".join(sorted(missing))
            raise ValueError(f"{step.step_id} is missing dimensions: {joined}")
        if extra:
            joined = ", ".join(sorted(extra))
            raise ValueError(f"{step.step_id} has unknown dimensions: {joined}")

        mode_scores = {
            mode: _score_mode(step, config, mode)
            for mode in config.mode_formulas
        }
        recommendation, gating_reason = _choose_recommendation(step, mode_scores, config)
        ranked_modes = tuple(sorted(mode_scores, key=mode_scores.get, reverse=True))
        scored_steps.append(
            ScoredStep(
                step=step,
                mode_scores=mode_scores,
                ranked_modes=ranked_modes,
                recommendation=recommendation,
                confidence=_confidence(mode_scores, step.dimension_value("evidence_strength")),
                top_mode_margin=_top_mode_margin(mode_scores),
                gating_reason=gating_reason,
                build_priority_score=_build_priority_score(step, recommendation, mode_scores),
            )
        )

    return scored_steps
