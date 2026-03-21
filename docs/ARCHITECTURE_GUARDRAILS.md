# AI Automation Surface Map Architecture Guardrails

## Scope Guardrails

- one workflow first
- one ranked decision surface first
- do not overbuild orchestration

## Data Guardrails

- Core objects:
  - `workflow`
  - `workflow_step`
  - `artifact`
  - `score`
  - `rationale`
- Keep observed workflow definitions separate from inferred score layers.
- Synthetic data that looks real is prohibited.

## Product Guardrails

- every score should support a build decision
- rationale matters as much as rank
- internal-tool usefulness is enough for v1

## Repo Guardrails

- Keep repo standalone.
- Prefer inspectable scoring and simple payloads.
- Avoid platform-level complexity before the internal loop proves useful.
