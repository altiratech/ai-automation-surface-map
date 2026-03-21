# AI Automation Surface Map

AI Automation Surface Map is a standalone repo scaffold hydrated from the KarpathyMerged materials.

## Product Center

This repo is building an internal strategy tool first, not the first standalone company.

The founding loop is:
1. choose one regulated workflow
2. decompose it into tasks and artifacts
3. score automation fit, human-signoff need, and liability asymmetry
4. use the result to guide product scope and agent design

## Current Repo Status

This repo now includes three locked workflow slices:
- one RIA marketing-rule review workflow
- one RIA annual Form ADV update workflow
- one RIA code-of-ethics personal trading exception-review workflow
- one static cross-slice pattern-summary artifact over those three workflows
- one static assist-lane reviewer-workbench slice over the shared judgment-heavy steps
- one explicit step and artifact model
- one inspectable Python scoring pipeline
- three published rationale-backed surface-map payloads
- one trust-review layer that checks source coverage before any UI work
- one thin React viewer that keeps the full drill-in on the marketing-review payload, exposes a compact annual ADV drill-in, and now includes a narrow local reviewer-workbench prototype for three pilot assist steps

## Canonical Build Truth

Treat these docs as authoritative:
- `docs/FOUNDING_PACKET.md`
- `docs/DEVELOPMENT_PACKET.md`
- `docs/BOOTSTRAP.md`
- `docs/FIRST_SLICE.md`
- `docs/IMPLEMENTATION_ENTRY_BRIEF.md`
- `docs/ARCHITECTURE_GUARDRAILS.md`

## Planned Repo Shape

- `configs/`
  - workflow templates and score definitions
- `data/`
  - captured workflow artifacts and normalized step data
- `pipeline/`
  - ingest, normalize, score, and publish logic
- `artifacts/`
  - ranked maps, score outputs, and review payloads
- `apps/api/`
  - thin orchestration surface when needed
- `apps/web/`
  - process map and ranked-step UI
- `packages/shared/`
  - shared contracts and schemas

## Build Rule

Do not force this into a broad standalone SaaS story.
Build it as a precise internal decision engine around one workflow at a time.

## Locked Workflow Commands

Generate the marketing-rule artifact payload:

```bash
/Users/ryanjameson/Desktop/Lifehub/.venv-fastlane/bin/python -m pipeline.publish
```

Generate the annual Form ADV update artifact payload:

```bash
/Users/ryanjameson/Desktop/Lifehub/.venv-fastlane/bin/python -m pipeline.publish_ria_annual_adv_update
```

Generate the code-of-ethics personal trading exception-review artifact payload:

```bash
/Users/ryanjameson/Desktop/Lifehub/.venv-fastlane/bin/python -m pipeline.publish_ria_code_of_ethics_exception_review
```

Generate the three-slice RIA pattern summary:

```bash
/Users/ryanjameson/Desktop/Lifehub/.venv-fastlane/bin/python -m pipeline.publish_ria_workflow_pattern_summary
```

Generate the shared assist-lane reviewer-workbench slice:

```bash
/Users/ryanjameson/Desktop/Lifehub/.venv-fastlane/bin/python -m pipeline.publish_ria_assist_lane_workbench_slice
```

Run the local verification suite:

```bash
/Users/ryanjameson/Desktop/Lifehub/.venv-fastlane/bin/python -m unittest discover -s tests
```

Published artifact:
- `artifacts/ria_marketing_rule_review.surface_map.json`
- `artifacts/ria_annual_adv_update.surface_map.json`
- `artifacts/ria_code_of_ethics_exception_review.surface_map.json`
- `artifacts/ria_workflow_pattern_summary.json`
- `artifacts/ria_assist_lane_workbench_slice.json`

Read-only web viewer:

```bash
cd apps/web
NPM_CONFIG_CACHE=/tmp/npm-cache npm install
NPM_CONFIG_CACHE=/tmp/npm-cache npm run dev
```

Current note:
- `apps/web` currently exposes the marketing-review detailed lane, the annual ADV compact lane, and a local reviewer-workbench prototype over one pilot assist step from each workflow.
- The detailed drill-in remains richest on the marketing-review workflow, with a smaller annual ADV drill-in now available in the same screen.
- The code-of-ethics exception-review workflow is now surfaced only through the pilot reviewer-workbench prototype, not through a broad workflow selector.
- The new pattern-summary artifact is a repo-side strategy output, not a new UI surface or workflow router.
- The new reviewer-workbench slice is also a repo-side design output; it defines the shared assist-lane surface before any broader UI implementation.
- This repo still does not support multi-workflow switching or orchestration in the UI.
