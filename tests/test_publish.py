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
            self.assertEqual(written["trust_summary"]["weakest_step"]["step_id"], "step-05-draft-review-memo-and-remediation")


if __name__ == "__main__":
    unittest.main()
