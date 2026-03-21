from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class ValidationError(ValueError):
    """Raised when repo-local workflow or scoring data is malformed."""


def _require_fields(raw: dict[str, Any], fields: tuple[str, ...], *, context: str) -> None:
    missing = [field for field in fields if field not in raw]
    if missing:
        raise ValidationError(f"{context} is missing required fields: {', '.join(missing)}")


def _validate_score(value: Any, *, context: str) -> int:
    if not isinstance(value, int):
        raise ValidationError(f"{context} must be an integer")
    if value < 0 or value > 100:
        raise ValidationError(f"{context} must be between 0 and 100")
    return value


def _unique_ids(items: list[Any], attr_name: str, *, context: str) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for item in items:
        item_id = getattr(item, attr_name)
        if item_id in seen:
            duplicates.add(item_id)
        seen.add(item_id)
    if duplicates:
        ordered = ", ".join(sorted(duplicates))
        raise ValidationError(f"{context} contains duplicate ids: {ordered}")


@dataclass(frozen=True)
class DimensionDefinition:
    key: str
    label: str
    description: str


@dataclass(frozen=True)
class FormulaTerm:
    weight: float
    direction: str

    @classmethod
    def from_raw(cls, raw: dict[str, Any], *, context: str) -> "FormulaTerm":
        _require_fields(raw, ("weight", "direction"), context=context)
        weight = raw["weight"]
        if not isinstance(weight, (int, float)):
            raise ValidationError(f"{context}.weight must be numeric")
        direction = raw["direction"]
        if direction not in {"direct", "inverse"}:
            raise ValidationError(f"{context}.direction must be 'direct' or 'inverse'")
        return cls(weight=float(weight), direction=direction)


@dataclass(frozen=True)
class ModeFormula:
    mode: str
    label: str
    terms: dict[str, FormulaTerm]

    @classmethod
    def from_raw(cls, mode: str, raw: dict[str, Any], *, context: str) -> "ModeFormula":
        _require_fields(raw, ("label", "terms"), context=context)
        terms_raw = raw["terms"]
        if not isinstance(terms_raw, dict):
            raise ValidationError(f"{context}.terms must be an object")
        terms = {
            key: FormulaTerm.from_raw(value, context=f"{context}.terms.{key}")
            for key, value in terms_raw.items()
        }
        total_weight = sum(term.weight for term in terms.values())
        if abs(total_weight - 1.0) > 0.001:
            raise ValidationError(f"{context}.terms weights must sum to 1.0")
        return cls(mode=mode, label=str(raw["label"]), terms=terms)


@dataclass(frozen=True)
class ScoringConfig:
    config_id: str
    version: str
    workflow_id: str
    dimensions: dict[str, DimensionDefinition]
    mode_formulas: dict[str, ModeFormula]
    gates: dict[str, int]

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "ScoringConfig":
        _require_fields(raw, ("config_id", "version", "workflow_id", "dimensions", "mode_formulas", "gates"), context="scoring config")
        dimensions_raw = raw["dimensions"]
        if not isinstance(dimensions_raw, dict):
            raise ValidationError("scoring config.dimensions must be an object")
        dimensions = {}
        for key, value in dimensions_raw.items():
            _require_fields(value, ("label", "description"), context=f"scoring config.dimensions.{key}")
            dimensions[key] = DimensionDefinition(
                key=key,
                label=str(value["label"]),
                description=str(value["description"]),
            )

        mode_formulas_raw = raw["mode_formulas"]
        if not isinstance(mode_formulas_raw, dict):
            raise ValidationError("scoring config.mode_formulas must be an object")
        mode_formulas = {
            mode: ModeFormula.from_raw(mode, value, context=f"scoring config.mode_formulas.{mode}")
            for mode, value in mode_formulas_raw.items()
        }
        for mode_formula in mode_formulas.values():
            unknown_dimensions = set(mode_formula.terms) - set(dimensions)
            if unknown_dimensions:
                unknown = ", ".join(sorted(unknown_dimensions))
                raise ValidationError(f"{mode_formula.mode} references unknown dimensions: {unknown}")

        gates_raw = raw["gates"]
        if not isinstance(gates_raw, dict):
            raise ValidationError("scoring config.gates must be an object")
        gates = {
            key: _validate_score(value, context=f"scoring config.gates.{key}")
            for key, value in gates_raw.items()
        }

        return cls(
            config_id=str(raw["config_id"]),
            version=str(raw["version"]),
            workflow_id=str(raw["workflow_id"]),
            dimensions=dimensions,
            mode_formulas=mode_formulas,
            gates=gates,
        )


@dataclass(frozen=True)
class EvidenceSource:
    source_id: str
    title: str
    source_type: str
    publisher: str
    published_date: str
    url: str
    summary: str

    @classmethod
    def from_raw(cls, raw: dict[str, Any], *, context: str) -> "EvidenceSource":
        _require_fields(raw, ("source_id", "title", "source_type", "publisher", "published_date", "url", "summary"), context=context)
        return cls(
            source_id=str(raw["source_id"]),
            title=str(raw["title"]),
            source_type=str(raw["source_type"]),
            publisher=str(raw["publisher"]),
            published_date=str(raw["published_date"]),
            url=str(raw["url"]),
            summary=str(raw["summary"]),
        )


@dataclass(frozen=True)
class ArtifactDefinition:
    artifact_id: str
    name: str
    artifact_type: str
    origin: str
    description: str
    step_ids: tuple[str, ...]

    @classmethod
    def from_raw(cls, raw: dict[str, Any], *, context: str) -> "ArtifactDefinition":
        _require_fields(raw, ("artifact_id", "name", "artifact_type", "origin", "description", "step_ids"), context=context)
        step_ids = raw["step_ids"]
        if not isinstance(step_ids, list) or not all(isinstance(item, str) for item in step_ids):
            raise ValidationError(f"{context}.step_ids must be a list of strings")
        return cls(
            artifact_id=str(raw["artifact_id"]),
            name=str(raw["name"]),
            artifact_type=str(raw["artifact_type"]),
            origin=str(raw["origin"]),
            description=str(raw["description"]),
            step_ids=tuple(step_ids),
        )


@dataclass(frozen=True)
class DimensionAssessment:
    value: int
    rationale: str

    @classmethod
    def from_raw(cls, raw: dict[str, Any], *, context: str) -> "DimensionAssessment":
        _require_fields(raw, ("value", "rationale"), context=context)
        return cls(
            value=_validate_score(raw["value"], context=f"{context}.value"),
            rationale=str(raw["rationale"]),
        )


@dataclass(frozen=True)
class EvidenceNote:
    source_id: str
    claim: str

    @classmethod
    def from_raw(cls, raw: dict[str, Any], *, context: str) -> "EvidenceNote":
        _require_fields(raw, ("source_id", "claim"), context=context)
        return cls(source_id=str(raw["source_id"]), claim=str(raw["claim"]))


@dataclass(frozen=True)
class WorkflowStep:
    step_id: str
    step_order: int
    step_name: str
    step_description: str
    human_owner_role: str
    artifact_ids: tuple[str, ...]
    source_ids: tuple[str, ...]
    hard_human_gate: bool
    dimension_scores: dict[str, DimensionAssessment]
    evidence_notes: tuple[EvidenceNote, ...]
    unknowns: tuple[str, ...]
    build_implication: str

    @classmethod
    def from_raw(cls, raw: dict[str, Any], *, context: str) -> "WorkflowStep":
        _require_fields(
            raw,
            (
                "step_id",
                "step_order",
                "step_name",
                "step_description",
                "human_owner_role",
                "artifact_ids",
                "source_ids",
                "hard_human_gate",
                "dimension_scores",
                "evidence_notes",
                "unknowns",
                "build_implication",
            ),
            context=context,
        )
        step_order = raw["step_order"]
        if not isinstance(step_order, int) or step_order <= 0:
            raise ValidationError(f"{context}.step_order must be a positive integer")
        artifact_ids = raw["artifact_ids"]
        if not isinstance(artifact_ids, list) or not all(isinstance(item, str) for item in artifact_ids):
            raise ValidationError(f"{context}.artifact_ids must be a list of strings")
        source_ids = raw["source_ids"]
        if not isinstance(source_ids, list) or not all(isinstance(item, str) for item in source_ids):
            raise ValidationError(f"{context}.source_ids must be a list of strings")
        hard_human_gate = raw["hard_human_gate"]
        if not isinstance(hard_human_gate, bool):
            raise ValidationError(f"{context}.hard_human_gate must be a boolean")
        dimensions_raw = raw["dimension_scores"]
        if not isinstance(dimensions_raw, dict):
            raise ValidationError(f"{context}.dimension_scores must be an object")
        dimension_scores = {
            key: DimensionAssessment.from_raw(value, context=f"{context}.dimension_scores.{key}")
            for key, value in dimensions_raw.items()
        }
        evidence_notes_raw = raw["evidence_notes"]
        if not isinstance(evidence_notes_raw, list):
            raise ValidationError(f"{context}.evidence_notes must be a list")
        evidence_notes = tuple(
            EvidenceNote.from_raw(note, context=f"{context}.evidence_notes[{index}]")
            for index, note in enumerate(evidence_notes_raw)
        )
        unknowns_raw = raw["unknowns"]
        if not isinstance(unknowns_raw, list) or not all(isinstance(item, str) for item in unknowns_raw):
            raise ValidationError(f"{context}.unknowns must be a list of strings")
        return cls(
            step_id=str(raw["step_id"]),
            step_order=step_order,
            step_name=str(raw["step_name"]),
            step_description=str(raw["step_description"]),
            human_owner_role=str(raw["human_owner_role"]),
            artifact_ids=tuple(artifact_ids),
            source_ids=tuple(source_ids),
            hard_human_gate=hard_human_gate,
            dimension_scores=dimension_scores,
            evidence_notes=evidence_notes,
            unknowns=tuple(unknowns_raw),
            build_implication=str(raw["build_implication"]),
        )

    def dimension_value(self, key: str) -> int:
        return self.dimension_scores[key].value


@dataclass(frozen=True)
class WorkflowDefinition:
    workflow_id: str
    workflow_name: str
    domain: str
    persona: str
    entry_condition: str
    completion_condition: str
    workflow_notes: tuple[str, ...]

    @classmethod
    def from_raw(cls, raw: dict[str, Any], *, context: str) -> "WorkflowDefinition":
        _require_fields(
            raw,
            (
                "workflow_id",
                "workflow_name",
                "domain",
                "persona",
                "entry_condition",
                "completion_condition",
                "workflow_notes",
            ),
            context=context,
        )
        notes = raw["workflow_notes"]
        if not isinstance(notes, list) or not all(isinstance(item, str) for item in notes):
            raise ValidationError(f"{context}.workflow_notes must be a list of strings")
        return cls(
            workflow_id=str(raw["workflow_id"]),
            workflow_name=str(raw["workflow_name"]),
            domain=str(raw["domain"]),
            persona=str(raw["persona"]),
            entry_condition=str(raw["entry_condition"]),
            completion_condition=str(raw["completion_condition"]),
            workflow_notes=tuple(notes),
        )


@dataclass(frozen=True)
class WorkflowBundle:
    workflow: WorkflowDefinition
    sources: dict[str, EvidenceSource]
    artifacts: dict[str, ArtifactDefinition]
    steps: tuple[WorkflowStep, ...]

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "WorkflowBundle":
        _require_fields(raw, ("workflow", "sources", "artifacts", "steps"), context="workflow bundle")
        workflow = WorkflowDefinition.from_raw(raw["workflow"], context="workflow bundle.workflow")

        sources_raw = raw["sources"]
        if not isinstance(sources_raw, list):
            raise ValidationError("workflow bundle.sources must be a list")
        sources = [
            EvidenceSource.from_raw(item, context=f"workflow bundle.sources[{index}]")
            for index, item in enumerate(sources_raw)
        ]
        _unique_ids(sources, "source_id", context="workflow bundle.sources")
        sources_by_id = {source.source_id: source for source in sources}

        artifacts_raw = raw["artifacts"]
        if not isinstance(artifacts_raw, list):
            raise ValidationError("workflow bundle.artifacts must be a list")
        artifacts = [
            ArtifactDefinition.from_raw(item, context=f"workflow bundle.artifacts[{index}]")
            for index, item in enumerate(artifacts_raw)
        ]
        _unique_ids(artifacts, "artifact_id", context="workflow bundle.artifacts")
        artifacts_by_id = {artifact.artifact_id: artifact for artifact in artifacts}

        steps_raw = raw["steps"]
        if not isinstance(steps_raw, list):
            raise ValidationError("workflow bundle.steps must be a list")
        steps = [
            WorkflowStep.from_raw(item, context=f"workflow bundle.steps[{index}]")
            for index, item in enumerate(steps_raw)
        ]
        _unique_ids(steps, "step_id", context="workflow bundle.steps")
        step_orders = [step.step_order for step in steps]
        if len(step_orders) != len(set(step_orders)):
            raise ValidationError("workflow bundle.steps contains duplicate step_order values")
        steps_by_id = {step.step_id: step for step in steps}

        for step in steps:
            for artifact_id in step.artifact_ids:
                if artifact_id not in artifacts_by_id:
                    raise ValidationError(f"{step.step_id} references unknown artifact id {artifact_id}")
            for source_id in step.source_ids:
                if source_id not in sources_by_id:
                    raise ValidationError(f"{step.step_id} references unknown source id {source_id}")
            for note in step.evidence_notes:
                if note.source_id not in sources_by_id:
                    raise ValidationError(f"{step.step_id} has evidence note for unknown source id {note.source_id}")

        for artifact in artifacts:
            for step_id in artifact.step_ids:
                if step_id not in steps_by_id:
                    raise ValidationError(f"{artifact.artifact_id} references unknown step id {step_id}")

        ordered_steps = tuple(sorted(steps, key=lambda step: step.step_order))
        return cls(
            workflow=workflow,
            sources=sources_by_id,
            artifacts=artifacts_by_id,
            steps=ordered_steps,
        )
