import { useState } from "react";

import surfaceMap from "@surface-map";

import type { RecommendationMode, StepResult, SurfaceMapPayload } from "./types";

const payload = surfaceMap as SurfaceMapPayload;

const modeMeta: Record<
  RecommendationMode,
  { label: string; tone: string; emphasis: string }
> = {
  automate: {
    label: "Automate",
    tone: "mode-automate",
    emphasis: "Structured edge work with low approval friction.",
  },
  assist: {
    label: "Assist",
    tone: "mode-assist",
    emphasis: "System support is valuable, but the human still owns the call.",
  },
  "keep-human": {
    label: "Keep Human",
    tone: "mode-keep-human",
    emphasis: "Use software for support only, not autonomous action.",
  },
};

const weakestStepId = payload.trust_summary.weakest_step.step_id;

function formatPercent(value: number): string {
  return `${Math.round(value * 100)}%`;
}

function scoreLabel(value: number): string {
  if (value >= 85) {
    return "very strong";
  }
  if (value >= 70) {
    return "strong";
  }
  if (value >= 55) {
    return "mixed";
  }
  return "weak";
}

function App() {
  const [selectedStepId, setSelectedStepId] = useState(weakestStepId);
  const selectedStep =
    payload.step_results.find((step) => step.step_id === selectedStepId) ??
    payload.step_results[0];

  return (
    <div className="page-shell">
      <header className="hero-panel">
        <div className="hero-copy">
          <p className="eyebrow">AI Automation Surface Map</p>
          <h1>{payload.workflow.workflow_name}</h1>
          <p className="hero-summary">{payload.summary.first_build_wedge}</p>
          <div className="workflow-meta">
            <span>{payload.workflow.domain}</span>
            <span>{payload.workflow.persona}</span>
          </div>
        </div>
        <div className="hero-status">
          <div className="metric-card accent-card">
            <span className="metric-label">Workflow Trust</span>
            <strong className="metric-value">
              {payload.trust_summary.workflow_trust_score}
            </strong>
            <span className="metric-footnote">
              Grade {payload.trust_summary.workflow_trust_grade}
            </span>
          </div>
          <div className="metric-card">
            <span className="metric-label">UI Readiness</span>
            <strong className="metric-value">
              {payload.trust_summary.read_only_ui_ready ? "Ready" : "Hold"}
            </strong>
            <span className="metric-footnote">
              {payload.trust_summary.blocking_items.length === 0
                ? "No blocking items"
                : `${payload.trust_summary.blocking_items.length} blockers`}
            </span>
          </div>
        </div>
      </header>

      <section className="summary-grid">
        <article className="panel mode-summary-panel">
          <div className="panel-heading">
            <p className="panel-kicker">Recommendation split</p>
            <h2>One workflow, one decision surface</h2>
          </div>
          <div className="mode-summary-grid">
            {(
              Object.keys(payload.summary.mode_counts) as RecommendationMode[]
            ).map((mode) => (
              <div key={mode} className={`mode-stat ${modeMeta[mode].tone}`}>
                <span className="mode-stat-count">
                  {payload.summary.mode_counts[mode]}
                </span>
                <span className="mode-stat-label">{modeMeta[mode].label}</span>
                <p>{modeMeta[mode].emphasis}</p>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <p className="panel-kicker">Build wedge</p>
            <h2>What to build first</h2>
          </div>
          <div className="callout-card">
            <p className="callout-label">Highest-priority buildable step</p>
            <strong>{payload.summary.highest_priority_build_step.step_name}</strong>
            <p>
              Recommendation:{" "}
              <span
                className={`inline-chip ${
                  modeMeta[payload.summary.highest_priority_build_step.recommendation].tone
                }`}
              >
                {modeMeta[payload.summary.highest_priority_build_step.recommendation].label}
              </span>
            </p>
          </div>
          <div className="callout-card warning-card">
            <p className="callout-label">Hard guardrail</p>
            <strong>{payload.summary.hard_guardrail_step.step_name}</strong>
            <p>{payload.summary.blocked_pattern}</p>
          </div>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <p className="panel-kicker">Review queue</p>
            <h2>What still deserves attention</h2>
          </div>
          <ul className="queue-list">
            {payload.trust_summary.review_queue.map((item) => (
              <li key={item.step_id}>
                <button
                  className="queue-item"
                  type="button"
                  onClick={() => setSelectedStepId(item.step_id)}
                >
                  <span className={`priority-pill priority-${item.priority}`}>
                    {item.priority}
                  </span>
                  <strong>{stepNameFor(item.step_id)}</strong>
                  <p>{item.action}</p>
                </button>
              </li>
            ))}
          </ul>
        </article>
      </section>

      <main className="workbench-grid">
        <section className="panel step-list-panel">
          <div className="panel-heading">
            <p className="panel-kicker">Workflow map</p>
            <h2>Step rail</h2>
          </div>
          <div className="step-list">
            {payload.step_results.map((step) => (
              <button
                key={step.step_id}
                className={`step-row ${
                  selectedStep.step_id === step.step_id ? "step-row-active" : ""
                }`}
                type="button"
                onClick={() => setSelectedStepId(step.step_id)}
              >
                <div className="step-row-order">{step.step_order}</div>
                <div className="step-row-copy">
                  <div className="step-row-head">
                    <strong>{step.step_name}</strong>
                    <span className={`inline-chip ${modeMeta[step.recommendation].tone}`}>
                      {modeMeta[step.recommendation].label}
                    </span>
                  </div>
                  <p>{step.human_owner_role}</p>
                </div>
                <div className="step-row-metrics">
                  <span>Trust {step.review.trust_score}</span>
                  <span>{formatPercent(step.confidence)}</span>
                </div>
              </button>
            ))}
          </div>
        </section>

        <section className="panel detail-panel">
          <div className="panel-heading">
            <p className="panel-kicker">Selected step</p>
            <h2>{selectedStep.step_name}</h2>
          </div>
          <p className="detail-summary">{selectedStep.step_description}</p>

          <div className="detail-chip-row">
            <span className={`inline-chip ${modeMeta[selectedStep.recommendation].tone}`}>
              {modeMeta[selectedStep.recommendation].label}
            </span>
            <span className="inline-chip neutral-chip">
              Build priority {selectedStep.build_priority_score}
            </span>
            <span className="inline-chip neutral-chip">
              Confidence {formatPercent(selectedStep.confidence)}
            </span>
            <span className="inline-chip neutral-chip">
              Trust {selectedStep.review.trust_score} / {selectedStep.review.trust_grade}
            </span>
          </div>

          <div className="detail-section-grid">
            <article className="subpanel">
              <h3>Decision rationale</h3>
              <p>{selectedStep.review.decision_rationale.why_this_mode}</p>
              <p>
                {selectedStep.review.decision_rationale.why_not_automate ??
                  selectedStep.review.decision_rationale.why_not_more_human}
              </p>
              <p className="muted-note">
                {selectedStep.review.decision_rationale.confidence_note}
              </p>
            </article>

            <article className="subpanel">
              <h3>Trust review</h3>
              <dl className="trust-metrics">
                <div>
                  <dt>Sources</dt>
                  <dd>{selectedStep.review.source_count}</dd>
                </div>
                <div>
                  <dt>Evidence notes</dt>
                  <dd>{selectedStep.review.evidence_note_count}</dd>
                </div>
                <div>
                  <dt>Artifacts</dt>
                  <dd>{selectedStep.review.artifact_count}</dd>
                </div>
                <div>
                  <dt>Top mode margin</dt>
                  <dd>{selectedStep.review.confidence_breakdown.top_mode_margin}</dd>
                </div>
              </dl>
              <p className="muted-note">{selectedStep.review.confidence_breakdown.note}</p>
              <div className="coverage-strip">
                {selectedStep.review.covered_dimensions.map((dimension) => (
                  <span key={dimension} className="coverage-pill">
                    {dimensionLabel(dimension)}
                  </span>
                ))}
              </div>
            </article>
          </div>

          <div className="detail-section-grid">
            <article className="subpanel">
              <h3>Dimension scores</h3>
              <div className="dimension-list">
                {Object.entries(selectedStep.dimension_scores).map(([key, dimension]) => (
                  <div key={key} className="dimension-row">
                    <div>
                      <strong>{dimension.label}</strong>
                      <p>{dimension.rationale}</p>
                    </div>
                    <div className="dimension-score">
                      <span>{dimension.value}</span>
                      <small>{scoreLabel(dimension.value)}</small>
                    </div>
                  </div>
                ))}
              </div>
            </article>

            <article className="subpanel">
              <h3>Review actions</h3>
              <ul className="simple-list">
                {selectedStep.review.review_actions.map((action) => (
                  <li key={action}>{action}</li>
                ))}
              </ul>
              <h3 className="secondary-heading">Unknowns</h3>
              <ul className="simple-list">
                {selectedStep.unknowns.map((unknown) => (
                  <li key={unknown}>{unknown}</li>
                ))}
              </ul>
            </article>
          </div>
        </section>

        <aside className="panel side-panel">
          <div className="panel-heading">
            <p className="panel-kicker">Evidence and outputs</p>
            <h2>Inspection lane</h2>
          </div>

          <section className="side-section">
            <h3>Artifacts in play</h3>
            <ul className="simple-list">
              {selectedStep.artifacts.map((artifact) => (
                <li key={artifact.artifact_id}>
                  <strong>{artifact.name}</strong>
                  <span>{artifact.artifact_type}</span>
                </li>
              ))}
            </ul>
          </section>

          <section className="side-section">
            <h3>Evidence notes</h3>
            <ul className="evidence-list">
              {selectedStep.evidence_notes.map((note) => (
                <li key={`${note.source_id}-${note.claim}`}>
                  <a href={note.source_url} target="_blank" rel="noreferrer">
                    {note.source_title}
                  </a>
                  <p>{note.claim}</p>
                  <div className="coverage-strip">
                    {note.supports_dimensions.map((dimension) => (
                      <span key={dimension} className="coverage-pill">
                        {dimensionLabel(dimension)}
                      </span>
                    ))}
                  </div>
                </li>
              ))}
            </ul>
          </section>

          <section className="side-section">
            <h3>Build decisions</h3>
            <ul className="decision-list">
              {payload.build_decisions.map((decision) => (
                <li key={decision.decision_type}>
                  <strong>{decision.decision}</strong>
                  <p>{decision.rationale}</p>
                </li>
              ))}
            </ul>
          </section>
        </aside>
      </main>
    </div>
  );
}

function stepNameFor(stepId: string): string {
  return payload.step_results.find((step) => step.step_id === stepId)?.step_name ?? stepId;
}

function dimensionLabel(dimension: string): string {
  return dimension.replaceAll("_", " ");
}

export default App;
