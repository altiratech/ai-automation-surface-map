# Artifacts

Use this folder for generated strategy outputs.

Tracked workflow artifacts:
- `ria_marketing_rule_review.surface_map.json`
- `ria_annual_adv_update.surface_map.json`
- `ria_code_of_ethics_exception_review.surface_map.json`

Tracked synthesis artifact:
- `ria_workflow_pattern_summary.json`

The payload now includes:
- per-step trust review sections
- workflow-level read-only UI readiness
- review queue items for the weakest-supported steps
- one repo-side cross-slice product-pattern summary

Regenerate the workflow artifacts with:
- `/Users/ryanjameson/Desktop/Lifehub/.venv-fastlane/bin/python -m pipeline.publish`
- `/Users/ryanjameson/Desktop/Lifehub/.venv-fastlane/bin/python -m pipeline.publish_ria_annual_adv_update`
- `/Users/ryanjameson/Desktop/Lifehub/.venv-fastlane/bin/python -m pipeline.publish_ria_code_of_ethics_exception_review`

Regenerate the synthesis artifact with:
- `/Users/ryanjameson/Desktop/Lifehub/.venv-fastlane/bin/python -m pipeline.publish_ria_workflow_pattern_summary`
