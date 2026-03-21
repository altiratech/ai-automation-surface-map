from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pipeline.publish import build_payload, publish


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
            self.assertGreaterEqual(written["trust_summary"]["workflow_trust_score"], 79)
            self.assertIn(
                written["trust_summary"]["weakest_step"]["step_id"],
                {item["step_id"] for item in written["step_results"]},
            )


if __name__ == "__main__":
    unittest.main()
