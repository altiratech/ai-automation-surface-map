export type RecommendationMode = "automate" | "assist" | "keep-human";
export type ReviewerOutcome = "confirm" | "revise" | "escalate";

export type SourceInventoryItem = {
  source_id: string;
  title: string;
  source_type: string;
  publisher: string;
  published_date: string;
  url: string;
  summary: string;
};

export type SurfaceMapPayload = {
  workflow: {
    workflow_id: string;
    workflow_name: string;
    domain: string;
    persona: string;
    entry_condition: string;
    completion_condition: string;
    workflow_notes: string[];
  };
  source_inventory: SourceInventoryItem[];
  summary: {
    mode_counts: Record<RecommendationMode, number>;
    first_build_wedge: string;
    highest_priority_build_step: {
      step_id: string;
      step_name: string;
      recommendation: RecommendationMode;
      build_priority_score: number;
    };
    hard_guardrail_step: {
      step_id: string;
      step_name: string;
      recommendation: RecommendationMode;
      build_priority_score: number;
    };
    lowest_confidence_step: {
      step_id: string;
      step_name: string;
      confidence: number;
    };
    blocked_pattern: string;
  };
  trust_summary: {
    workflow_trust_score: number;
    workflow_trust_grade: string;
    read_only_ui_ready: boolean;
    weakest_step: {
      step_id: string;
      trust_score: number;
    };
    review_queue: Array<{
      step_id: string;
      priority: string;
      action: string;
    }>;
    blocking_items: string[];
  };
  build_decisions: Array<{
    decision_type: string;
    decision: string;
    step_ids: string[];
    rationale: string;
  }>;
  step_results: StepResult[];
};

export type StepResult = {
  step_id: string;
  step_order: number;
  step_name: string;
  step_description: string;
  human_owner_role: string;
  recommendation: RecommendationMode;
  mode_scores: Record<RecommendationMode, number>;
  ranked_modes: RecommendationMode[];
  build_priority_score: number;
  confidence: number;
  hard_human_gate: boolean;
  gating_reason: string | null;
  artifacts: Array<{
    artifact_id: string;
    name: string;
    artifact_type: string;
  }>;
  dimension_scores: Record<
    string,
    {
      label: string;
      value: number;
      rationale: string;
    }
  >;
  evidence_notes: Array<{
    source_id: string;
    source_title: string;
    source_url: string;
    claim: string;
    supports_dimensions: string[];
  }>;
  unknowns: string[];
  build_implication: string;
  review: {
    trust_score: number;
    trust_grade: string;
    source_count: number;
    evidence_note_count: number;
    artifact_count: number;
    covered_dimensions: string[];
    missing_dimensions: string[];
    unknown_count: number;
    read_only_ui_ready: boolean;
    confidence_breakdown: {
      confidence: number;
      top_mode_margin: number;
      evidence_strength: number;
      note: string;
    };
    decision_rationale: {
      why_this_mode: string;
      why_not_more_human?: string;
      why_not_automate?: string;
      confidence_note: string;
    };
    review_actions: string[];
  };
};

export type AssistLaneWorkbenchPayload = {
  scope: {
    workflow_count: number;
    assist_step_count: number;
    pilot_step_count: number;
    source_artifacts: string[];
    pattern_summary_artifact: string;
  };
  workbench_thesis: {
    thesis: string;
    reason: string;
  };
  supporting_steps: Array<{
    workflow_id: string;
    workflow_name: string;
    step_id: string;
    step_name: string;
    build_priority_score: number;
    review_action: string | null;
    build_implication: string;
  }>;
  pilot_steps: Array<{
    workflow_id: string;
    workflow_name: string;
    step_id: string;
    step_name: string;
    build_priority_score: number;
    review_action: string | null;
    build_implication: string;
  }>;
  shared_jobs_to_be_done: Array<{
    job_id: string;
    job: string;
    backed_by_fields: string[];
  }>;
  v1_sections: Array<{
    section_id: string;
    title: string;
    purpose: string;
    uses_fields: string[];
  }>;
  reviewer_confirmation_pattern: {
    steps_requiring_explicit_confirmation: Array<{
      workflow_id: string;
      step_id: string;
      step_name: string;
      action: string;
    }>;
    count: number;
  };
};
