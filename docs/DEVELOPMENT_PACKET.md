# AI Automation Surface Map Development Packet

Status: hydrated repo-local build packet

## Purpose

This file captures the richer original detail behind the automation-surface idea so the repo can be developed as a self-sufficient internal product strategy tool without repeatedly reopening the Karpathy source folders.

## Source Materials Absorbed

- `Business Ideas/01_Karpathy/KarpathyMerged/app_ideas_catalog.md`
- `Business Ideas/01_Karpathy/KarpathyMerged/karpathy1_idea_lineage.md`
- `Business Ideas/01_Karpathy/KarpathyMerged/founder_context_and_selection_constraints.md`
- `Business Ideas/01_Karpathy/KarpathyMerged/implementation_blueprint.md`
- `Business Ideas/01_Karpathy/KarpathyMerged/merged_concepts.md`

## Product Thesis

Break one regulated workflow into tasks and artifacts, then score each step for automation feasibility, human sign-off need, liability asymmetry, and customer pain.

This repo is allowed to be an internal engine first.
It does not need to prove standalone monetization before it becomes useful.

## Why This Exists

- product drift is expensive in regulated domains
- many teams know they want AI help but cannot explain which steps should be automated, assisted, or left human
- task-level clarity can directly sharpen what gets built in the other repos

## First Users

Primary early users:
- internal product strategist
- builder working on regulated-ops software
- founder choosing the right automation wedge

Possible later external users:
- compliance software buyers
- operators evaluating where automation is safe and useful

## Job To Be Done

Find which workflow steps should be automated now, assisted, or kept human.

## Canonical Object

Primary object:
- `workflow_step`

Supporting objects:
- workflow
- artifact or document
- score dimension
- rationale

This repo is not centered on:
- lead lists
- accounts
- generic flowcharting

## Lineage And Strategic Role

Primary lineage:
- `Function-to-Workflow Atlas`
  - survives here as the strongest internal engine form

Important adjacent relationships:
- `ria_inflection_engine`
  - this tool can sharpen which RIA workflow modules get built after the signal layer
- `ria_operating_stress_os`
  - this merged vision explicitly depends on automation-surface logic once the inflection loop is proven

## Recommended First Workflow

Pick one regulated workflow only.

Best preserved starting examples from the source packet:
- RIA launch workflow
- marketing-rule review workflow

Avoid starting with:
- a multi-domain workflow universe
- generic process-mining posture

## Data Source Inventory

Useful public source anchors for the first RIA-oriented workflow:
- Form ADV Part 2 Data Files
  - example source artifacts and disclosure structure
- SEC 2026 Examination Priorities
  - current pressure themes
- SEC Risk Alerts
  - current pressure themes

Additional inputs the tool is allowed to use:
- explicit workflow definitions
- curated task decompositions
- local artifact examples

## Data Truth Rules

- source evidence and workflow coverage claims must never be fabricated
- task definitions may be observed or carefully curated
- scores are inferred
- score confidence and unknowns should be shown explicitly
- the product should separate observed artifacts from inferred step-level automation guidance

## Scoring Model

Core score dimensions:
- automation feasibility
- liability asymmetry
- human-signoff necessity
- data availability
- customer pain
- frequency

Output categories should support:
- automate
- assist
- keep human

Preferred interpretation rule:
- preserve nuance
- do not force every step into full automation

## Canonical Schema

### `workflows`
- `workflow_id`
- `workflow_name`
- `domain`
- `entry_condition`
- `completion_condition`

### `workflow_steps`
- `step_id`
- `workflow_id`
- `step_name`
- `step_order`
- `step_description`
- `human_owner_role`

### `artifacts`
- `artifact_id`
- `workflow_id`
- `step_id`
- `artifact_name`
- `artifact_type`
- `source_url`
- `notes`

### `step_scores`
- `score_id`
- `step_id`
- `automation_feasibility`
- `liability_asymmetry`
- `human_signoff_necessity`
- `data_availability`
- `customer_pain`
- `frequency`
- `recommended_mode`
- `confidence`
- `rationale`

### `score_evidence`
- `evidence_id`
- `score_id`
- `artifact_id`
- `source_type`
- `snippet_text`
- `evidence_role`

## UI Guidance

Primary expression:
- process graph or workflow map

Secondary views:
- ranked step list
- rationale panel
- artifact detail
- mode split by automate, assist, keep human

Do not let the first product become:
- a generic flowchart app
- a generic consulting deck generator
- a broad analytics layer with no build-decision output

## First User Workflow

1. choose one workflow
2. model the steps and artifacts
3. score each step
4. view a ranked build recommendation
5. use the result to shape product or agent priorities

## MVP Build Sequence

Phase 0:
- choose the first workflow
- define the step and artifact ontology
- define scoring dimensions

Phase 1:
- model one workflow map and its artifacts
- capture explicit evidence and unknowns

Phase 2:
- implement scoring and rationale generation
- produce automate vs assist vs human recommendations

Phase 3:
- build a workflow map plus ranked action surface
- support drill-in rationale and evidence

Phase 4:
- use the results to shape one adjacent build track
- validate whether the output changes real roadmap decisions

## Success Definition

The tool is successful when the user can:
- inspect one workflow
- see which steps are good automation candidates
- understand why some steps should stay human
- leave with a clearer product or agent roadmap

## Key Risks

Product risks:
- becoming generic workflow software
- becoming a consulting-output generator
- producing abstract advice that does not change what gets built

Model risks:
- shallow workflow decomposition
- overconfident automation recommendations
- failing to distinguish assist from automate

Scope risks:
- trying to support too many workflows too early

## Validation Checklist

1. Choose one first workflow and one persona.
2. Validate the step list with a real artifact set.
3. Test whether the score output changes a concrete build decision.
4. Check that at least one step clearly lands in each of automate, assist, and keep human.
5. Ensure rationale stays grounded in evidence and not generic AI language.

## Placeholder Rule

Use:
- empty workflow arrays
- explicit workflow coverage notes
- `placeholder: true` where needed

Do not use:
- invented evidence snippets
- fake coverage claims
- synthetic workflow confidence without rationale

## Local Repo Translation

Current local scaffold:
- `apps/api/`
- `apps/web/`
- `packages/shared/`
- `docs/`
- `scripts/`
- `tests/`

Recommended implementation expansion:
- `configs/`
  - scoring definitions and workflow templates
- `data/`
  - captured workflow artifacts and normalized step data
- `pipeline/`
  - ingest, normalize, score, publish
- `artifacts/`
  - ranked workflow maps and review payloads

Working rule:
- keep the product truth in explicit workflow/step/artifact structures
- do not let UI polish get ahead of the scoring and rationale model
