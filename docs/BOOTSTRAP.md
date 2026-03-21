# AI Automation Surface Map Bootstrap Contract

Status: locked for scaffold-phase kickoff

## Toolchain Decision

- Python work uses the shared fastlane environment at `/Users/ryanjameson/Desktop/Lifehub/.venv-fastlane`.
- JavaScript work uses `npm` only after real code lands in `apps/web` or `packages/shared`.
- Slice 1 is Python-first and local-only.
- Slice 1 does not require a database or deployment target.

## Start Rule

1. Start in `configs/`, `data/`, and `pipeline/`.
2. Keep `apps/web` parked until one workflow map plus scored action payload exists.
3. Add `packages/shared` only when both scoring and UI need the same contract.

## First Executable Contract

Before any UI work, produce:
- one workflow definition
- one step and artifact model
- one scored action payload
- one rationale payload under `artifacts/`

## Explicit Defers

Do not start with:
- `npm install`
- multi-workflow support
- agent orchestration
- auth
- deployment setup
