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

This repo now includes the first locked slice:
- one RIA marketing-rule review workflow
- one explicit step and artifact model
- one inspectable Python scoring pipeline
- one published rationale-backed surface-map payload
- one trust-review layer that checks source coverage before any UI work

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

## First Slice Commands

Generate the local artifact payload:

```bash
/Users/ryanjameson/Desktop/Lifehub/.venv-fastlane/bin/python -m pipeline.publish
```

Run the local verification suite:

```bash
/Users/ryanjameson/Desktop/Lifehub/.venv-fastlane/bin/python -m unittest discover -s tests
```

Published artifact:
- `artifacts/ria_marketing_rule_review.surface_map.json`
