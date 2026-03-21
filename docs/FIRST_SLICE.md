# AI Automation Surface Map First Slice

Status: locked kickoff slice

## Goal

Map one real regulated workflow end to end, score each step, and publish a clear automate vs assist vs keep-human recommendation set.

## Locked Decisions

- First workflow: RIA marketing-rule review.
- First persona: internal product strategist mapping the workflow used by an outsourced compliance provider.
- First UI mode: no app until the scored workflow payload is trustworthy.
- First score dimensions:
  - automation fit
  - human sign-off need
  - liability asymmetry
  - evidence strength

## First Source Set

- one explicit workflow map
- one set of representative artifacts used in review
- one evidence-backed rationale set per step

## First Files To Touch

- `configs/`
- `data/`
- `pipeline/`
- `artifacts/`
- `tests/`

## Done When

- one workflow can be decomposed into steps and artifacts
- each step lands in automate, assist, or keep-human with rationale
- at least one build decision changes because of the output
- the payload is strong enough that a UI would only be a presentation layer

## Not Yet

- multi-workflow comparison
- external user support
- deep agent orchestration
- broad analytics
