# AI Automation Surface Map Implementation Entry Brief

Purpose: keep the first engineering passes focused on one usable internal decision loop.

## Current Product Center

Build the smallest serious loop:

1. choose one workflow
2. model steps and artifacts
3. score each step for automation suitability
4. produce a ranked build recommendation

## First Build Blocks

### 1. Data model foundation

Lock schemas for:
- workflows
- workflow steps
- artifacts
- score dimensions
- rationales

### 2. Core APIs or payloads

Initial product access should support:
- workflow view
- ranked step list
- rationale panel

### 3. Web surfaces

Initial web surfaces should support:
- process map or step list
- ranked action surface
- drill-in rationale

## Explicit Defers

Do not treat these as founding blockers:
- multi-workflow comparison
- external user support
- heavy agent orchestration
- broad analytics layer

## Design Guardrail

This tool should feel like a precise internal strategy workbench, not a generic flowchart app.
