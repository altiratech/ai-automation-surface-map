# Web App

Intended responsibilities:
- workflow map or step list
- ranked recommendations
- rationale drill-in

Current slice:
- read-only React + TypeScript viewer over the published marketing-review surface-map artifact
- compact read-only drill-in for the annual Form ADV update artifact in the same screen
- the code-of-ethics exception-review workflow is now publishable in the repo, but not yet surfaced in the UI
- no scoring logic in the UI
- no write paths, auth, or orchestration

Current non-goal:
- no multi-workflow switching in the UI yet; the second locked workflow is inspectable, while the third remains artifact-only until we deliberately expand the viewer

Local commands:
- `NPM_CONFIG_CACHE=/tmp/npm-cache npm install`
- `NPM_CONFIG_CACHE=/tmp/npm-cache npm run dev`
- `NPM_CONFIG_CACHE=/tmp/npm-cache npm run build`
