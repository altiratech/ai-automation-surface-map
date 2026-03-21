# AI Automation Surface Map Founding Packet

Status: canonical current-scope document

## 1. Project

- Project name: AI Automation Surface Map
- Owner: Ryan Jameson
- Date opened: 2026-03-20
- Status: scaffolded

## 2. One-Sentence Product Definition

`This product helps a builder or product strategist decide what parts of one regulated workflow to automate, assist, or leave human using task-level scoring, without pretending to be a standalone horizontal AI platform on day one.`

## 3. First User

- Primary user: internal product strategist or builder working on regulated-ops products
- What they are trying to get done: choose the highest-value automation wedge
- What they do today instead: intuition, scattered docs, and ad hoc workflow lists
- Why they would switch: this tool creates a more explicit and inspectable decision layer

## 4. First Workflow

1. user picks one regulated workflow
2. user decomposes it into tasks and artifacts
3. user sees scored automation suitability for each step
4. user leaves with a ranked build or agent-design priority list

## 5. Canonical Object

- Canonical object: `workflow_step`
- Why this is the product center: the tool is about task-level decisions, not whole companies or markets
- What is explicitly not the canonical object: lead, account, or firm

## 6. Current Scope

- In scope:
  - one workflow map
  - task and artifact model
  - automation scoring
  - ranked recommendations

## 7. Explicit Non-Goals

- Not in scope now:
  - broad horizontal AI platform
  - external sales product
  - deep agent runtime or orchestration layer

## 8. Do-Not-Drift-Into

- Drift risks to avoid:
  - generic process-mining software
  - consulting deliverable generator
  - abstract workflow taxonomy with no build decision output

## 9. Approved Terminology

| Use | Avoid | Why |
|---|---|---|
| `workflow step` | `job` | keeps the tool grounded in productizable work units |
| `assist` | `automate` everywhere | preserves nuance |
| `liability asymmetry` | `risk` only | keeps the scoring sharper |

## 10. Repo / Architecture Pattern

- Repo shape: standalone mono-repo scaffold
- Frontend stack: React + TypeScript
- Backend stack: Python-first scoring and artifact generation
- Shared contracts: `packages/shared`
- Deployment target: local-first internal tool
- Explicitly rejected patterns:
  - enterprise platform scope
  - agent-runtime overbuild before the scoring model works

## 11. Data Truth Rules

- Source of truth: workflow decomposition, official source artifacts where relevant, and explicit task definitions
- What is observed vs inferred: task definitions can be observed or curated, scores are inferred
- What can be missing: confidence and coverage
- What must never be faked: source evidence or workflow coverage claims
- How uncertainty should be shown: score confidence plus explicit unknowns

## 12. Quality Gates

- Required validation:
  - workflow map is coherent
  - scoring dimensions are explicit
  - output leads to a real product prioritization decision

## 13. First 2-4 Week Build Sequence

| Order | Build block | Why now |
|---|---|---|
| 1 | choose first workflow and object model | keeps scope real |
| 2 | build step/artifact schema | product center |
| 3 | implement scoring and rationale | core value |
| 4 | build ranked workflow map UI | decision surface |

## 14. Open Questions That Do Not Block Start

- Open but non-blocking:
  - kickoff decisions are now locked in `docs/FIRST_SLICE.md`
  - whether to support multiple personas in v1
  - whether this should stay internal permanently

## 15. Go / No-Go Check Before Real Code

- [x] one-sentence product definition is stable
- [x] first user is specific
- [x] first workflow is specific
- [x] canonical object is clear
- [x] non-goals are written down
- [x] terminology is coherent
- [x] repo pattern is chosen
- [x] data truth rules are defined
