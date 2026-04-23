# AI Automation Surface Map

AI Automation Surface Map is a decision engine for decomposing regulated workflows and identifying where software, agents, or human review should sit.

This repo is intentionally an internal-strategy tool first. It is not being forced into a broad standalone SaaS product before the workflow-mapping loop is trusted.

## Product Center

The founding loop is:
1. choose one regulated workflow
2. decompose it into tasks and artifacts
3. score automation fit, human-signoff need, and liability asymmetry
4. use the result to guide product scope and agent design

## Status

Implemented local slices currently cover:
- RIA marketing-rule review
- RIA annual Form ADV update
- RIA code-of-ethics personal trading exception review
- a cross-slice pattern-summary artifact
- a shared assist-lane reviewer-workbench slice
- an inspectable Python scoring pipeline
- a thin React viewer for selected workflow and reviewer-workbench outputs

## Quick Start

```bash
git clone https://github.com/altiratech/ai-automation-surface-map.git
cd ai-automation-surface-map
```

Generate the locked workflow artifacts:

```bash
python3 -m pipeline.publish
python3 -m pipeline.publish_ria_annual_adv_update
python3 -m pipeline.publish_ria_code_of_ethics_exception_review
python3 -m pipeline.publish_ria_workflow_pattern_summary
python3 -m pipeline.publish_ria_assist_lane_workbench_slice
```

Run tests:

```bash
python3 -m unittest discover -s tests
```

Run the read-only web viewer:

```bash
cd apps/web
npm install
npm run dev
```

## Published Artifacts

- `artifacts/ria_marketing_rule_review.surface_map.json`
- `artifacts/ria_annual_adv_update.surface_map.json`
- `artifacts/ria_code_of_ethics_exception_review.surface_map.json`
- `artifacts/ria_workflow_pattern_summary.json`
- `artifacts/ria_assist_lane_workbench_slice.json`

## Repo Shape

```text
configs/         workflow templates and score definitions
data/            captured workflow artifacts and normalized step data
pipeline/        ingest, normalize, score, review, and publish logic
artifacts/       ranked maps, score outputs, and review payloads
apps/web/        read-only viewer
docs/            build truth and guardrails
tests/           pipeline and artifact tests
```

## Build Rule

Build this as a precise decision engine around one workflow at a time. Do not widen into multi-workflow orchestration until the narrow assist-lane and scoring contracts are reliable.

## License

No open-source license has been selected yet. Public source visibility does not grant reuse rights until a license file is added.
