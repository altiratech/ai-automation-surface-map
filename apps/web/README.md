# Web App

Intended responsibilities:
- workflow map or step list
- ranked recommendations
- rationale drill-in

Current slice:
- read-only React + TypeScript viewer over the published marketing-review surface-map artifact
- compact read-only drill-in for the annual Form ADV update artifact in the same screen
- no scoring logic in the UI
- no write paths, auth, or orchestration

Current non-goal:
- no multi-workflow switching in the UI yet; the second locked workflow is inspectable, but still not an interactive workflow selector

Local commands:
- `NPM_CONFIG_CACHE=/tmp/npm-cache npm install`
- `NPM_CONFIG_CACHE=/tmp/npm-cache npm run dev`
- `NPM_CONFIG_CACHE=/tmp/npm-cache npm run build`
