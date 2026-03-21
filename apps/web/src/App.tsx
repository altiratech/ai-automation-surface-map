import { useState } from "react";

import surfaceMap from "@surface-map";
import annualSurfaceMap from "@surface-map-annual";
import codeEthicsSurfaceMap from "@surface-map-code-ethics";
import assistWorkbenchSlice from "@assist-workbench-slice";

import type {
  AssistLaneWorkbenchPayload,
  RecommendationMode,
  ReviewerOutcome,
  SourceInventoryItem,
  StepResult,
  SurfaceMapPayload,
} from "./types";

const payload = surfaceMap as SurfaceMapPayload;
const annualPayload = annualSurfaceMap as SurfaceMapPayload;
const codeEthicsPayload = codeEthicsSurfaceMap as SurfaceMapPayload;
const assistWorkbench = assistWorkbenchSlice as AssistLaneWorkbenchPayload;
const portfolioPayloads = [payload, annualPayload, codeEthicsPayload];

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
const annualWeakestStepId = annualPayload.trust_summary.weakest_step.step_id;
const defaultWorkbenchPilotStepId = assistWorkbench.pilot_steps[0]?.step_id ?? "";

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

function formatDateLabel(value: string): string {
  const parsed = new Date(`${value}T00:00:00Z`);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(parsed);
}

function workflowStatusLabel(item: SurfaceMapPayload): string {
  return item.trust_summary.read_only_ui_ready ? "Ready" : "Hold";
}

function workflowLaneLabel(item: SurfaceMapPayload): string {
  if (item.workflow.workflow_id === payload.workflow.workflow_id) {
    return "Detailed lane";
  }
  if (item.workflow.workflow_id === annualPayload.workflow.workflow_id) {
    return "Compact lane";
  }
  return "Workbench lane";
}

function outcomeLabel(outcome: ReviewerOutcome): string {
  return outcome.charAt(0).toUpperCase() + outcome.slice(1);
}

function stepNameForPayload(item: SurfaceMapPayload, stepId: string): string {
  return item.step_results.find((step) => step.step_id === stepId)?.step_name ?? stepId;
}

function cautionCountForPayload(item: SurfaceMapPayload): number {
  return item.step_results.filter((step) => step.review.review_actions.length > 0).length;
}

function humanGateCountForPayload(item: SurfaceMapPayload): number {
  return item.step_results.filter((step) => step.hard_human_gate).length;
}

function trustCompleteCountForPayload(item: SurfaceMapPayload): number {
  return item.step_results.filter((step) => step.review.trust_score >= 80).length;
}

function App() {
  const [selectedStepId, setSelectedStepId] = useState(weakestStepId);
  const [selectedAnnualStepId, setSelectedAnnualStepId] = useState(annualWeakestStepId);
  const [selectedWorkbenchStepId, setSelectedWorkbenchStepId] = useState(
    defaultWorkbenchPilotStepId,
  );
  const [workbenchDrafts, setWorkbenchDrafts] = useState<Record<string, string>>({});
  const [workbenchReasons, setWorkbenchReasons] = useState<Record<string, string>>({});
  const [workbenchOutcomes, setWorkbenchOutcomes] = useState<
    Partial<Record<string, ReviewerOutcome>>
  >({});
  const selectedStep =
    payload.step_results.find((step) => step.step_id === selectedStepId) ??
    payload.step_results[0];
  const selectedAnnualStep =
    annualPayload.step_results.find((step) => step.step_id === selectedAnnualStepId) ??
    annualPayload.step_results[0];
  const workbenchPayloadLookup: Record<string, SurfaceMapPayload> = {
    [payload.workflow.workflow_id]: payload,
    [annualPayload.workflow.workflow_id]: annualPayload,
    [codeEthicsPayload.workflow.workflow_id]: codeEthicsPayload,
  };
  const selectedQueueItem = payload.trust_summary.review_queue.find(
    (item) => item.step_id === selectedStep.step_id,
  );
  const selectedAnnualQueueItem = annualPayload.trust_summary.review_queue.find(
    (item) => item.step_id === selectedAnnualStep.step_id,
  );
  const sourceLookup = Object.fromEntries(
    payload.source_inventory.map((source) => [source.source_id, source]),
  ) as Record<string, SourceInventoryItem>;
  const annualSourceLookup = Object.fromEntries(
    annualPayload.source_inventory.map((source) => [source.source_id, source]),
  ) as Record<string, SourceInventoryItem>;
  const codeEthicsSourceLookup = Object.fromEntries(
    codeEthicsPayload.source_inventory.map((source) => [source.source_id, source]),
  ) as Record<string, SourceInventoryItem>;
  const workbenchSourceLookupByWorkflow: Record<
    string,
    Record<string, SourceInventoryItem>
  > = {
    [payload.workflow.workflow_id]: sourceLookup,
    [annualPayload.workflow.workflow_id]: annualSourceLookup,
    [codeEthicsPayload.workflow.workflow_id]: codeEthicsSourceLookup,
  };
  const isWeakestTrustStep = selectedStep.step_id === weakestStepId;
  const isLowestConfidenceStep =
    selectedStep.step_id === payload.summary.lowest_confidence_step.step_id;
  const stepsAboveTrustFloor = payload.step_results.filter(
    (step) => step.review.trust_score >= 80,
  ).length;
  const totalUnknowns = payload.step_results.reduce(
    (total, step) => total + step.review.unknown_count,
    0,
  );
  const activeCautionCount = payload.step_results.filter(
    (step) => step.review.review_actions.length > 0,
  ).length;
  const hardHumanGateCount = payload.step_results.filter(
    (step) => step.hard_human_gate,
  ).length;
  const primaryReviewAction =
    selectedQueueItem?.action ??
    selectedStep.review.review_actions[0] ??
    "No remaining caution in the current slice.";
  const annualPrimaryReviewAction =
    selectedAnnualQueueItem?.action ??
    selectedAnnualStep.review.review_actions[0] ??
    "No remaining caution in this workflow.";
  const annualWeakestStepName = stepNameForPayload(
    annualPayload,
    annualPayload.trust_summary.weakest_step.step_id,
  );
  const selectedWorkbenchPilot =
    assistWorkbench.pilot_steps.find((step) => step.step_id === selectedWorkbenchStepId) ??
    assistWorkbench.pilot_steps[0];
  const selectedWorkbenchPayload =
    workbenchPayloadLookup[selectedWorkbenchPilot.workflow_id] ?? payload;
  const selectedWorkbenchStep =
    selectedWorkbenchPayload.step_results.find(
      (step) => step.step_id === selectedWorkbenchPilot.step_id,
    ) ?? selectedWorkbenchPayload.step_results[0];
  const selectedWorkbenchSourceLookup =
    workbenchSourceLookupByWorkflow[selectedWorkbenchPilot.workflow_id] ?? sourceLookup;
  const relatedAssistSteps = assistWorkbench.supporting_steps.filter(
    (step) => step.workflow_id === selectedWorkbenchPilot.workflow_id,
  );
  const workbenchDraft =
    workbenchDrafts[selectedWorkbenchStep.step_id] ??
    [
      selectedWorkbenchStep.review.decision_rationale.why_this_mode,
      selectedWorkbenchStep.review.review_actions[0],
      selectedWorkbenchStep.build_implication,
    ]
      .filter((value): value is string => Boolean(value))
      .join("\n\n");
  const workbenchReason = workbenchReasons[selectedWorkbenchStep.step_id] ?? "";
  const workbenchOutcome = workbenchOutcomes[selectedWorkbenchStep.step_id];
  const workbenchNeedsExplicitConfirmation =
    assistWorkbench.reviewer_confirmation_pattern.steps_requiring_explicit_confirmation.some(
      (step) =>
        step.workflow_id === selectedWorkbenchPilot.workflow_id &&
        step.step_id === selectedWorkbenchStep.step_id,
    );
  const nextHumanGate = selectedWorkbenchPayload.summary.hard_guardrail_step;

  return (
    <div className="page-shell">
      <section className="portfolio-strip">
        <div className="portfolio-heading">
          <p className="eyebrow">Locked Workflow Portfolio</p>
          <h2>Three validated slices, one still-narrow prototype surface</h2>
          <p className="portfolio-summary">
            The app still avoids a broad workflow selector. It now shows the original detailed
            lane, the annual compact lane, and a narrow reviewer-workbench prototype fed by one
            pilot assist step from each workflow.
          </p>
        </div>
        <div className="portfolio-grid">
          {portfolioPayloads.map((item) => (
            <article key={item.workflow.workflow_id} className="portfolio-card">
              <div className="portfolio-card-head">
                <div>
                  <p className="panel-kicker">Locked workflow</p>
                  <h3>{item.workflow.workflow_name}</h3>
                </div>
                <span className="inline-chip neutral-chip">{workflowLaneLabel(item)}</span>
              </div>
              <p className="portfolio-card-summary">{item.summary.first_build_wedge}</p>
              <div className="portfolio-metrics">
                <div>
                  <span>Trust</span>
                  <strong>{item.trust_summary.workflow_trust_score}</strong>
                </div>
                <div>
                  <span>UI readiness</span>
                  <strong>{workflowStatusLabel(item)}</strong>
                </div>
                <div>
                  <span>Trust-complete steps</span>
                  <strong>
                    {trustCompleteCountForPayload(item)}/{item.step_results.length}
                  </strong>
                </div>
                <div>
                  <span>Active cautions</span>
                  <strong>{cautionCountForPayload(item)}</strong>
                </div>
                <div>
                  <span>Human-only gates</span>
                  <strong>{humanGateCountForPayload(item)}</strong>
                </div>
                <div>
                  <span>Weakest step</span>
                  <strong>
                    {stepNameForPayload(item, item.trust_summary.weakest_step.step_id)}
                  </strong>
                </div>
              </div>
              <div className="portfolio-mode-row">
                {(Object.keys(item.summary.mode_counts) as RecommendationMode[]).map((mode) => (
                  <span key={mode} className={`inline-chip ${modeMeta[mode].tone}`}>
                    {modeMeta[mode].label}: {item.summary.mode_counts[mode]}
                  </span>
                ))}
              </div>
              <div className="portfolio-note">
                <span className="callout-label">Top build step</span>
                <strong>{item.summary.highest_priority_build_step.step_name}</strong>
              </div>
            </article>
          ))}
        </div>
      </section>

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

      <section className="trust-story-strip">
        <article className="trust-story-card">
          <span className="callout-label">Trust-complete steps</span>
          <strong>
            {stepsAboveTrustFloor}/{payload.step_results.length}
          </strong>
          <p>Every step is now above the low-80 trust floor for this locked workflow.</p>
        </article>
        <article className="trust-story-card">
          <span className="callout-label">Open unknowns</span>
          <strong>{totalUnknowns}</strong>
          <p>Firm-policy variation is now modeled as configuration, not unresolved debt.</p>
        </article>
        <article className="trust-story-card">
          <span className="callout-label">Active cautions</span>
          <strong>{activeCautionCount}</strong>
          <p>Only substantive reviewer cautions remain in the queue.</p>
        </article>
        <article className="trust-story-card">
          <span className="callout-label">Human-only gates</span>
          <strong>{hardHumanGateCount}</strong>
          <p>The publication approval decision still stays explicitly human.</p>
        </article>
      </section>

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
          <p className="queue-note">
            The queue now shows only steps with remaining reviewer action, not resolved edge
            assumptions.
          </p>
          <div className="queue-summary">
            <button
              className="queue-summary-card"
              type="button"
              onClick={() => setSelectedStepId(payload.trust_summary.weakest_step.step_id)}
            >
              <span className="callout-label">Weakest trust</span>
              <strong>{stepNameFor(payload.trust_summary.weakest_step.step_id)}</strong>
              <p>Trust {payload.trust_summary.weakest_step.trust_score}</p>
            </button>
            <button
              className="queue-summary-card"
              type="button"
              onClick={() =>
                setSelectedStepId(payload.summary.lowest_confidence_step.step_id)
              }
            >
              <span className="callout-label">Lowest confidence</span>
              <strong>{payload.summary.lowest_confidence_step.step_name}</strong>
              <p>{formatPercent(payload.summary.lowest_confidence_step.confidence)}</p>
            </button>
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

      <section className="secondary-snapshot-grid">
        <article className="panel annual-snapshot-panel">
          <div className="panel-heading">
            <p className="panel-kicker">Second locked workflow</p>
            <h2>{annualPayload.workflow.workflow_name}</h2>
          </div>
          <p className="detail-summary">{annualPayload.summary.first_build_wedge}</p>
          <div className="annual-highlight-grid">
            <div className="callout-card">
              <p className="callout-label">Highest-priority buildable step</p>
              <strong>{annualPayload.summary.highest_priority_build_step.step_name}</strong>
              <p>
                Recommendation:{" "}
                <span
                  className={`inline-chip ${
                    modeMeta[annualPayload.summary.highest_priority_build_step.recommendation].tone
                  }`}
                >
                  {modeMeta[annualPayload.summary.highest_priority_build_step.recommendation].label}
                </span>
              </p>
            </div>
            <div className="callout-card warning-card">
              <p className="callout-label">Hard guardrail</p>
              <strong>{annualPayload.summary.hard_guardrail_step.step_name}</strong>
              <p>{annualPayload.summary.blocked_pattern}</p>
            </div>
          </div>
          <div className="annual-detail-grid">
            <article className="subpanel">
              <h3>Current review queue</h3>
              <ul className="queue-list compact-queue-list">
                {annualPayload.trust_summary.review_queue.map((item) => (
                  <li key={item.step_id}>
                    <div className="queue-item static-queue-item">
                      <span className={`priority-pill priority-${item.priority}`}>
                        {item.priority}
                      </span>
                      <strong>{stepNameForPayload(annualPayload, item.step_id)}</strong>
                      <p>{item.action}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </article>
            <article className="subpanel">
              <h3>Why this matters</h3>
              <p>
                This second artifact proves the scoring model can handle a different RIA workflow
                shape without adding orchestration, workflow switching, or browser-side scoring.
              </p>
              <p>
                The remaining caution concentration is where we would expect it:
                brochure/disclosure reconciliation and the filing-signoff gate.
              </p>
              <div className="detail-chip-row">
                <span className="inline-chip neutral-chip">
                  Weakest step: {annualWeakestStepName}
                </span>
                <span className="inline-chip neutral-chip">
                  Trust {annualPayload.trust_summary.workflow_trust_score}
                </span>
                <span className="inline-chip neutral-chip">
                  Read-only {workflowStatusLabel(annualPayload)}
                </span>
              </div>
            </article>
          </div>
          <div className="annual-drillin-grid">
            <article className="subpanel">
              <h3>Annual step lane</h3>
              <div className="annual-step-list">
                {annualPayload.step_results.map((step) => (
                  <button
                    key={step.step_id}
                    className={`annual-step-row ${
                      selectedAnnualStep.step_id === step.step_id
                        ? "annual-step-row-active"
                        : ""
                    }`}
                    type="button"
                    onClick={() => setSelectedAnnualStepId(step.step_id)}
                  >
                    <div>
                      <strong>{step.step_name}</strong>
                      <p>{step.human_owner_role}</p>
                    </div>
                    <div className="annual-step-metrics">
                      <span className={`inline-chip ${modeMeta[step.recommendation].tone}`}>
                        {modeMeta[step.recommendation].label}
                      </span>
                      <span className="inline-chip neutral-chip">
                        Trust {step.review.trust_score}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            </article>
            <article className="subpanel">
              <h3>{selectedAnnualStep.step_name}</h3>
              <p>{selectedAnnualStep.step_description}</p>
              <div className="detail-chip-row">
                <span
                  className={`inline-chip ${modeMeta[selectedAnnualStep.recommendation].tone}`}
                >
                  {modeMeta[selectedAnnualStep.recommendation].label}
                </span>
                {selectedAnnualStep.hard_human_gate ? (
                  <span className="inline-chip mode-keep-human">Hard human gate</span>
                ) : null}
                <span className="inline-chip neutral-chip">
                  Confidence {formatPercent(selectedAnnualStep.confidence)}
                </span>
                <span className="inline-chip neutral-chip">
                  Build priority {selectedAnnualStep.build_priority_score}
                </span>
              </div>
              <div className="snapshot-list annual-snapshot-list">
                <div className="snapshot-row">
                  <span>Owner</span>
                  <strong>{selectedAnnualStep.human_owner_role}</strong>
                </div>
                <div className="snapshot-row">
                  <span>Primary review action</span>
                  <p>{annualPrimaryReviewAction}</p>
                </div>
                <div className="snapshot-row">
                  <span>Build implication</span>
                  <p>{selectedAnnualStep.build_implication}</p>
                </div>
              </div>
              <div className="annual-mini-grid">
                <section>
                  <h3 className="secondary-heading">Artifacts in play</h3>
                  <ul className="simple-list compact-simple-list">
                    {selectedAnnualStep.artifacts.map((artifact) => (
                      <li key={artifact.artifact_id}>
                        <strong>{artifact.name}</strong>
                        <span>{artifact.artifact_type}</span>
                      </li>
                    ))}
                  </ul>
                </section>
                <section>
                  <h3 className="secondary-heading">Evidence notes</h3>
                  <ul className="evidence-list compact-evidence-list">
                    {selectedAnnualStep.evidence_notes.map((note) => (
                      <li key={`${note.source_id}-${note.claim}`}>
                        <div className="evidence-head">
                          <a href={note.source_url} target="_blank" rel="noreferrer">
                            {note.source_title}
                          </a>
                          <div className="evidence-meta">
                            <span className="inline-chip neutral-chip">
                              {annualSourceLookup[note.source_id]?.source_type ?? "source"}
                            </span>
                            <span className="inline-chip neutral-chip">
                              {formatDateLabel(
                                annualSourceLookup[note.source_id]?.published_date ?? "",
                              )}
                            </span>
                          </div>
                        </div>
                        <p>{note.claim}</p>
                      </li>
                    ))}
                  </ul>
                </section>
              </div>
            </article>
          </div>
        </article>
      </section>

      <section className="panel reviewer-prototype-panel">
        <div className="panel-heading">
          <p className="panel-kicker">Local prototype</p>
          <h2>Shared reviewer workbench for assist-lane steps</h2>
        </div>
        <p className="detail-summary">{assistWorkbench.workbench_thesis.thesis}</p>
        <p className="muted-note workbench-summary-note">
          {assistWorkbench.workbench_thesis.reason}
        </p>
        <div className="detail-chip-row">
          <span className="inline-chip neutral-chip">
            {assistWorkbench.scope.assist_step_count} assist steps
          </span>
          <span className="inline-chip neutral-chip">
            {assistWorkbench.scope.pilot_step_count} pilot steps
          </span>
          <span className="inline-chip neutral-chip">
            {assistWorkbench.reviewer_confirmation_pattern.count} explicit confirmation steps
          </span>
        </div>

        <div className="reviewer-prototype-grid reviewer-prototype-top">
          <article className="subpanel">
            <h3>Pilot queue</h3>
            <p className="muted-note">
              One top assist step per workflow. This is intentionally narrower than a general
              workflow selector.
            </p>
            <div className="pilot-step-list">
              {assistWorkbench.pilot_steps.map((step) => (
                <button
                  key={step.step_id}
                  className={`pilot-step-card ${
                    selectedWorkbenchStep.step_id === step.step_id
                      ? "pilot-step-card-active"
                      : ""
                  }`}
                  type="button"
                  onClick={() => setSelectedWorkbenchStepId(step.step_id)}
                >
                  <span className="callout-label">{step.workflow_name}</span>
                  <strong>{step.step_name}</strong>
                  <p>{step.build_implication}</p>
                  <div className="pilot-step-foot">
                    <span className="inline-chip mode-assist">Assist</span>
                    <span className="inline-chip neutral-chip">
                      Build priority {step.build_priority_score}
                    </span>
                  </div>
                </button>
              ))}
            </div>
            <div className="detail-chip-row prototype-section-row">
              {assistWorkbench.v1_sections.map((section) => (
                <span key={section.section_id} className="inline-chip neutral-chip">
                  {section.title}
                </span>
              ))}
            </div>
          </article>

          <article className="subpanel">
            <h3>Selected step context</h3>
            <p>{selectedWorkbenchStep.step_description}</p>
            <div className="detail-chip-row">
              <span className="inline-chip neutral-chip">
                {selectedWorkbenchPilot.workflow_name}
              </span>
              <span className={`inline-chip ${modeMeta[selectedWorkbenchStep.recommendation].tone}`}>
                {modeMeta[selectedWorkbenchStep.recommendation].label}
              </span>
              <span className="inline-chip neutral-chip">
                Trust {selectedWorkbenchStep.review.trust_score}
              </span>
              <span className="inline-chip neutral-chip">
                Confidence {formatPercent(selectedWorkbenchStep.confidence)}
              </span>
              {workbenchNeedsExplicitConfirmation ? (
                <span className="inline-chip mode-assist">Reviewer confirmation</span>
              ) : null}
            </div>
            <div className="snapshot-list workbench-context-list">
              <div className="snapshot-row">
                <span>Owner</span>
                <strong>{selectedWorkbenchStep.human_owner_role}</strong>
              </div>
              <div className="snapshot-row">
                <span>Why assist</span>
                <p>{selectedWorkbenchStep.review.decision_rationale.why_this_mode}</p>
              </div>
              <div className="snapshot-row">
                <span>Current caution</span>
                <p>
                  {selectedWorkbenchStep.review.review_actions[0] ??
                    "No active caution for this pilot step."}
                </p>
              </div>
            </div>
            <h3 className="secondary-heading">Same-workflow support steps</h3>
            <ul className="simple-list compact-simple-list">
              {relatedAssistSteps.map((step) => (
                <li key={step.step_id}>
                  <strong>{step.step_name}</strong>
                  <span>{step.build_implication}</span>
                </li>
              ))}
            </ul>
          </article>
        </div>

        <div className="reviewer-prototype-grid reviewer-prototype-main">
          <article className="subpanel">
            <h3>Evidence</h3>
            <div className="workbench-evidence-grid">
              <section>
                <h4>Artifacts in play</h4>
                <ul className="simple-list compact-simple-list">
                  {selectedWorkbenchStep.artifacts.map((artifact) => (
                    <li key={artifact.artifact_id}>
                      <strong>{artifact.name}</strong>
                      <span>{artifact.artifact_type}</span>
                    </li>
                  ))}
                </ul>
              </section>
              <section>
                <h4>Evidence notes</h4>
                <ul className="evidence-list compact-evidence-list">
                  {selectedWorkbenchStep.evidence_notes.map((note) => (
                    <li key={`${note.source_id}-${note.claim}`}>
                      <div className="evidence-head">
                        <a href={note.source_url} target="_blank" rel="noreferrer">
                          {note.source_title}
                        </a>
                        <div className="evidence-meta">
                          <span className="inline-chip neutral-chip">
                            {selectedWorkbenchSourceLookup[note.source_id]?.source_type ??
                              "source"}
                          </span>
                          <span className="inline-chip neutral-chip">
                            {formatDateLabel(
                              selectedWorkbenchSourceLookup[note.source_id]?.published_date ??
                                "",
                            )}
                          </span>
                        </div>
                      </div>
                      <p>{note.claim}</p>
                    </li>
                  ))}
                </ul>
              </section>
            </div>
          </article>

          <article className="subpanel">
            <h3>Draft</h3>
            <p className="muted-note">
              Local-only prototype state. The browser keeps the working draft for this session,
              but nothing is written back to a server.
            </p>
            <textarea
              className="workbench-textarea"
              value={workbenchDraft}
              onChange={(event) =>
                setWorkbenchDrafts((current) => ({
                  ...current,
                  [selectedWorkbenchStep.step_id]: event.target.value,
                }))
              }
            />
            <div className="workbench-support-list">
              {assistWorkbench.shared_jobs_to_be_done.map((job) => (
                <div key={job.job_id} className="support-card">
                  <strong>{job.job}</strong>
                  <p>{job.backed_by_fields.join(", ")}</p>
                </div>
              ))}
            </div>
          </article>

          <article className="subpanel">
            <h3>Decision</h3>
            <p className="muted-note">
              The prototype records a reviewer outcome locally, then points to the next human gate
              instead of auto-resolving the workflow.
            </p>
            <div className="outcome-button-row">
              {(["confirm", "revise", "escalate"] as ReviewerOutcome[]).map((outcome) => (
                <button
                  key={outcome}
                  className={`outcome-button ${
                    workbenchOutcome === outcome ? "outcome-button-active" : ""
                  }`}
                  type="button"
                  onClick={() =>
                    setWorkbenchOutcomes((current) => ({
                      ...current,
                      [selectedWorkbenchStep.step_id]: outcome,
                    }))
                  }
                >
                  {outcomeLabel(outcome)}
                </button>
              ))}
            </div>
            <textarea
              className="workbench-textarea workbench-textarea-compact"
              placeholder="Why are you confirming, revising, or escalating this step?"
              value={workbenchReason}
              onChange={(event) =>
                setWorkbenchReasons((current) => ({
                  ...current,
                  [selectedWorkbenchStep.step_id]: event.target.value,
                }))
              }
            />
            <div className="snapshot-list workbench-context-list">
              <div className="snapshot-row">
                <span>Current outcome</span>
                <strong>{workbenchOutcome ? outcomeLabel(workbenchOutcome) : "Not set"}</strong>
              </div>
              <div className="snapshot-row">
                <span>Next human gate</span>
                <p>{nextHumanGate.step_name}</p>
              </div>
              <div className="snapshot-row">
                <span>Why this stays human</span>
                <p>{selectedWorkbenchPayload.summary.blocked_pattern}</p>
              </div>
            </div>
          </article>
        </div>
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
                    <span
                      className={`inline-chip ${
                        step.review.review_actions.length === 0
                          ? "step-status-clear"
                          : "step-status-caution"
                      }`}
                    >
                      {step.review.review_actions.length === 0 ? "Cleared" : "Caution"}
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
            {selectedStep.hard_human_gate ? (
              <span className="inline-chip mode-keep-human">Hard human gate</span>
            ) : null}
            {isWeakestTrustStep ? (
              <span className="inline-chip neutral-chip">Weakest trust step</span>
            ) : null}
            {isLowestConfidenceStep ? (
              <span className="inline-chip neutral-chip">Lowest confidence step</span>
            ) : null}
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

          <div className="snapshot-grid">
            <article className="subpanel emphasis-subpanel">
              <h3>Fast read</h3>
              <div className="snapshot-list">
                <div className="snapshot-row">
                  <span>Owner</span>
                  <strong>{selectedStep.human_owner_role}</strong>
                </div>
                <div className="snapshot-row">
                  <span>Primary review action</span>
                  <p>{primaryReviewAction}</p>
                </div>
                <div className="snapshot-row">
                  <span>Build implication</span>
                  <p>{selectedStep.build_implication}</p>
                </div>
                <div className="snapshot-row">
                  <span>Queue status</span>
                  <strong>
                    {selectedQueueItem
                      ? `${selectedQueueItem.priority} priority`
                      : "Not in active review queue"}
                  </strong>
                </div>
              </div>
            </article>

            <article className="subpanel">
              <h3>Mode spread</h3>
              <p className="muted-note">
                The bar view makes the recommendation easier to inspect when two modes are
                close.
              </p>
              <div className="mode-bar-list">
                {selectedStep.ranked_modes.map((mode) => (
                  <div key={mode} className="mode-bar-row">
                    <div className="mode-bar-head">
                      <span className={`inline-chip ${modeMeta[mode].tone}`}>
                        {modeMeta[mode].label}
                      </span>
                      <strong>{selectedStep.mode_scores[mode]}</strong>
                    </div>
                    <div className="mode-bar-track">
                      <div
                        className={`mode-bar-fill ${modeMeta[mode].tone}`}
                        style={{ width: `${selectedStep.mode_scores[mode]}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </article>
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
                  <div className="evidence-head">
                    <a href={note.source_url} target="_blank" rel="noreferrer">
                      {note.source_title}
                    </a>
                    <div className="evidence-meta">
                      <span className="inline-chip neutral-chip">
                        {sourceLookup[note.source_id]?.source_type ?? "source"}
                      </span>
                      <span className="inline-chip neutral-chip">
                        {formatDateLabel(
                          sourceLookup[note.source_id]?.published_date ?? "",
                        )}
                      </span>
                    </div>
                  </div>
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
  return stepNameForPayload(payload, stepId);
}

function dimensionLabel(dimension: string): string {
  return dimension.replaceAll("_", " ");
}

export default App;
