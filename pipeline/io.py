from __future__ import annotations

import json
from pathlib import Path

from .models import ScoringConfig, WorkflowBundle


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_scoring_config(path: Path) -> ScoringConfig:
    return ScoringConfig.from_raw(load_json(path))


def load_workflow_bundle(path: Path) -> WorkflowBundle:
    return WorkflowBundle.from_raw(load_json(path))
