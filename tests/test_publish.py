from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pipeline.publish import build_payload, publish
from pipeline.publish_ria_annual_adv_update import (
    build_payload as build_second_payload,
    publish as publish_second,
)
from pipeline.publish_ria_code_of_ethics_exception_review import (
    build_payload as build_third_payload,
    publish as publish_third,
)


class FirstSlicePublishTests(unittest.TestCase):
    def test_step_recommendations_cover_all_three_modes(self) -> None:
        payload = build_payload()
        recommendations = {item["recommendation"] for item in payload["step_results"]}
        self.assertEqual(recommendations, {"automate", "assist", "keep-human"})

    def test_final_approval_stays_human(self) -> None:
        payload = build_payload()
        approval_step = next(
            item for item in payload["step_results"] if item["step_id"] == "step-06-principal-approval"
        )
        self.assertEqual(approval_step["recommendation"], "keep-human")
        self.assertEqual(approval_step["gating_reason"], "hard-human-gate")
        self.assertIn(
            "approval support",
            approval_step["review"]["review_actions"][-1],
        )

    def test_trust_review_enables_read_only_ui_and_covers_all_dimensions(self) -> None:
        payload = build_payload()
        self.assertTrue(payload["trust_summary"]["read_only_ui_ready"])
        for step in payload["step_results"]:
            self.assertEqual(step["review"]["missing_dimensions"], [])
            self.assertGreaterEqual(step["review"]["source_count"], 3)
            self.assertEqual(step["review"]["unknown_count"], 0)

    def test_step_five_uses_latest_sec_faq_and_retains_assist_posture(self) -> None:
        payload = build_payload()
        source_ids = {item["source_id"] for item in payload["source_inventory"]}
        self.assertIn("sec_marketing_rule_faq_2026", source_ids)

        remediation_step = next(
            item for item in payload["step_results"] if item["step_id"] == "step-05-draft-review-memo-and-remediation"
        )
        self.assertEqual(remediation_step["recommendation"], "assist")
        self.assertGreaterEqual(remediation_step["review"]["trust_score"], 79)
        self.assertGreaterEqual(remediation_step["review"]["evidence_note_count"], 4)
        self.assertIn(
            "sec_marketing_rule_faq_2026",
            {note["source_id"] for note in remediation_step["evidence_notes"]},
        )

    def test_step_two_uses_edge_case_sources_and_retains_assist_posture(self) -> None:
        payload = build_payload()
        classification_step = next(
            item for item in payload["step_results"] if item["step_id"] == "step-02-classify-advertisement"
        )
        self.assertEqual(classification_step["recommendation"], "assist")
        self.assertGreaterEqual(classification_step["review"]["trust_score"], 80)
        self.assertGreaterEqual(classification_step["review"]["evidence_note_count"], 4)
        step_two_sources = {note["source_id"] for note in classification_step["evidence_notes"]}
        self.assertIn("sec_marketing_rule_exam_alert_2023", step_two_sources)
        self.assertIn("sec_marketing_rule_faq_2026", step_two_sources)

    def test_step_six_keeps_human_gate_with_supervisory_source_support(self) -> None:
        payload = build_payload()
        approval_step = next(
            item for item in payload["step_results"] if item["step_id"] == "step-06-principal-approval"
        )
        self.assertEqual(approval_step["recommendation"], "keep-human")
        self.assertTrue(approval_step["hard_human_gate"])
        self.assertGreaterEqual(approval_step["review"]["trust_score"], 80)
        self.assertGreaterEqual(approval_step["review"]["evidence_note_count"], 4)
        self.assertIn(
            "sec_marketing_rule_exam_alert_2022",
            {note["source_id"] for note in approval_step["evidence_notes"]},
        )

    def test_publish_writes_surface_map_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "surface_map.json"
            payload = publish(output_path=output_path)
            self.assertTrue(output_path.exists())
            written = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(written["artifact_id"], "ria_marketing_rule_review_surface_map")
            self.assertEqual(written["summary"]["mode_counts"]["keep-human"], 1)
            self.assertEqual(payload["build_decisions"][-1]["decision_type"], "enforce-human-gate")
            self.assertIn("workflow_trust_score", written["trust_summary"])
            self.assertGreaterEqual(written["trust_summary"]["workflow_trust_score"], 82)
            self.assertIn(
                written["trust_summary"]["weakest_step"]["step_id"],
                {item["step_id"] for item in written["step_results"]},
            )
            for queue_item in written["trust_summary"]["review_queue"]:
                self.assertNotEqual(queue_item["action"], "No immediate action required.")


class SecondWorkflowPublishTests(unittest.TestCase):
    def test_second_workflow_uses_all_three_modes_without_broadening_scope(self) -> None:
        payload = build_second_payload()
        self.assertEqual(payload["workflow"]["workflow_id"], "ria-annual-adv-update")
        self.assertEqual(
            payload["summary"]["mode_counts"],
            {"automate": 3, "assist": 3, "keep-human": 1},
        )
        self.assertIn("annual filing mechanics", payload["summary"]["first_build_wedge"])

    def test_registration_basis_step_uses_current_edge_case_source(self) -> None:
        payload = build_second_payload()
        registration_step = next(
            item
            for item in payload["step_results"]
            if item["step_id"] == "step-02-reconcile-registration-basis-and-profile-fields"
        )
        self.assertEqual(registration_step["recommendation"], "assist")
        self.assertGreaterEqual(registration_step["review"]["trust_score"], 80)
        self.assertIn(
            "sec_internet_adviser_reforms_2024",
            {note["source_id"] for note in registration_step["evidence_notes"]},
        )

    def test_submission_step_stays_human_with_public_filing_support(self) -> None:
        payload = build_second_payload()
        submission_step = next(
            item
            for item in payload["step_results"]
            if item["step_id"] == "step-06-authorize-and-submit-annual-amendment"
        )
        self.assertEqual(submission_step["recommendation"], "keep-human")
        self.assertTrue(submission_step["hard_human_gate"])
        self.assertGreaterEqual(submission_step["review"]["trust_score"], 80)
        self.assertIn(
            "sec_form_adv_form_2024",
            {note["source_id"] for note in submission_step["evidence_notes"]},
        )
        self.assertIn(
            "approval support",
            submission_step["review"]["review_actions"][-1],
        )

    def test_second_workflow_publish_writes_expected_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "surface_map_second.json"
            payload = publish_second(output_path=output_path)
            self.assertTrue(output_path.exists())
            written = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(written["artifact_id"], "ria_annual_adv_update_surface_map")
            self.assertEqual(written["generated_by"], "/Users/ryanjameson/Desktop/Lifehub/.venv-fastlane/bin/python -m pipeline.publish_ria_annual_adv_update")
            self.assertGreaterEqual(written["trust_summary"]["workflow_trust_score"], 80)
            self.assertEqual(payload["build_decisions"][-1]["decision_type"], "enforce-human-gate")
            for step in written["step_results"]:
                self.assertEqual(step["review"]["missing_dimensions"], [])
                self.assertGreaterEqual(step["review"]["source_count"], 3)
                self.assertEqual(step["review"]["unknown_count"], 0)
            for queue_item in written["trust_summary"]["review_queue"]:
                self.assertNotEqual(queue_item["action"], "No immediate action required.")


class ThirdWorkflowPublishTests(unittest.TestCase):
    def test_third_workflow_uses_all_three_modes_and_stays_within_scope(self) -> None:
        payload = build_third_payload()
        self.assertEqual(payload["workflow"]["workflow_id"], "ria-code-of-ethics-exception-review")
        self.assertEqual(
            payload["summary"]["mode_counts"],
            {"automate": 3, "assist": 3, "keep-human": 1},
        )
        self.assertIn("monitoring rails", payload["summary"]["first_build_wedge"])

    def test_access_person_scope_step_uses_recent_exam_source_and_stays_assist(self) -> None:
        payload = build_third_payload()
        scope_step = next(
            item
            for item in payload["step_results"]
            if item["step_id"] == "step-02-confirm-access-person-scope"
        )
        self.assertEqual(scope_step["recommendation"], "assist")
        self.assertGreaterEqual(scope_step["review"]["trust_score"], 80)
        self.assertIn(
            "sec_code_of_ethics_risk_alert_2022",
            {note["source_id"] for note in scope_step["evidence_notes"]},
        )

    def test_cco_adjudication_step_stays_human_with_rule_release_support(self) -> None:
        payload = build_third_payload()
        adjudication_step = next(
            item
            for item in payload["step_results"]
            if item["step_id"] == "step-06-cco-adjudication-and-sanctions-decision"
        )
        self.assertEqual(adjudication_step["recommendation"], "keep-human")
        self.assertTrue(adjudication_step["hard_human_gate"])
        self.assertGreaterEqual(adjudication_step["review"]["trust_score"], 80)
        self.assertIn(
            "sec_code_of_ethics_rule_release_2004",
            {note["source_id"] for note in adjudication_step["evidence_notes"]},
        )
        self.assertIn(
            "approval support",
            adjudication_step["review"]["review_actions"][-1],
        )

    def test_third_workflow_publish_writes_expected_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "surface_map_third.json"
            payload = publish_third(output_path=output_path)
            self.assertTrue(output_path.exists())
            written = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(written["artifact_id"], "ria_code_of_ethics_exception_review_surface_map")
            self.assertEqual(
                written["generated_by"],
                "/Users/ryanjameson/Desktop/Lifehub/.venv-fastlane/bin/python -m pipeline.publish_ria_code_of_ethics_exception_review",
            )
            self.assertGreaterEqual(written["trust_summary"]["workflow_trust_score"], 80)
            self.assertEqual(payload["build_decisions"][-1]["decision_type"], "enforce-human-gate")
            for step in written["step_results"]:
                self.assertEqual(step["review"]["missing_dimensions"], [])
                self.assertGreaterEqual(step["review"]["source_count"], 3)
                self.assertEqual(step["review"]["unknown_count"], 0)
            for queue_item in written["trust_summary"]["review_queue"]:
                self.assertNotEqual(queue_item["action"], "No immediate action required.")


if __name__ == "__main__":
    unittest.main()
