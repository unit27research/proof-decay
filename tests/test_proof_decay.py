import unittest

from proof_decay import analyze_decay, extract_claims, parse_proof_notes, render_markdown


CLAIMS = """# Release Claims

The workflow is ready for public release.

The model is safe for hospitals.
"""

PROOF_NOTES = """# Proof Notes

## Proof: local demo screenshot
- evidence artifact: local demo screenshot
- artifact date: 2025-10-01
- evidence strength: artifact-backed
- evidence type: screenshot
- scope supported: local demo on synthetic prompts
- freshness window: 30 days
- changed conditions: code changed after screenshot; no current CI run
- limitations: no production deployment; no external users
- corroboration status: none

## Proof: hospital checklist
- evidence artifact: local checklist
- artifact date: 2025-09-15
- evidence strength: artifact-backed
- evidence type: local checklist
- scope supported: local checklist against sample prompts
- freshness window: 14 days
- changed conditions: model prompt changed; no clinical review
- limitations: no patient data; no hospital pilot; no external validation
- corroboration status: none
"""


class ProofDecayTests(unittest.TestCase):
    def test_stale_artifact_flags_proof_decay_and_proofwashing(self):
        review = analyze_decay(CLAIMS, PROOF_NOTES, review_date="2026-05-26")

        self.assertEqual(len(review["reviews"]), 2)

        first = review["reviews"][0]
        self.assertEqual(first["claim_line"], 3)
        self.assertIn("proof_decay", first["decay_flag"])
        self.assertIn("stale_artifact", first["decay_flag"])
        self.assertIn("proofwashing", first["risk_flag"])
        self.assertIn("2025-10-01", first["evidence_artifact"])
        self.assertIn("local demo on synthetic prompts", first["bounded_wording"])
        self.assertIn("does not establish current release readiness", first["bounded_wording"])

        second = review["reviews"][1]
        self.assertIn("medical_or_clinical_safety", second["risk_flag"])
        self.assertIn("does not establish current medical or clinical safety", second["bounded_wording"])

    def test_structured_proof_note_parsing(self):
        notes = parse_proof_notes(PROOF_NOTES)

        self.assertEqual(len(notes), 2)
        self.assertEqual(notes[0].label, "local demo screenshot")
        self.assertEqual(notes[0].artifact_date.isoformat(), "2025-10-01")
        self.assertEqual(notes[0].freshness_window_days, 30)
        self.assertIn("code changed", notes[0].changed_conditions)

    def test_ordered_fallback_is_marked_low_confidence(self):
        review = analyze_decay(
            "The parser is safe for hospitals.",
            """## Proof: unrelated demo
- evidence artifact: unrelated local screenshot
- artifact date: 2026-05-20
- evidence strength: artifact-backed
- evidence type: screenshot
- scope supported: local billing export
- freshness window: 30 days
- changed conditions: none
- limitations: no clinical review
- corroboration status: none
""",
            review_date="2026-05-26",
        )

        first = review["reviews"][0]
        self.assertEqual(first["match_basis"], "ordered_fallback")
        self.assertIn("low_confidence_match", first["decay_flag"])
        self.assertIn("Verify that the matched proof note belongs to this claim", first["next_verification_step"])

    def test_missing_and_invalid_artifact_dates_do_not_crash(self):
        missing = analyze_decay(
            "The workflow is ready for public release.",
            """## Proof: missing date
- evidence artifact: local screenshot
- evidence strength: artifact-backed
- evidence type: screenshot
- scope supported: local demo
- freshness window: 30 days
""",
            review_date="2026-05-26",
        )
        self.assertIn("missing_artifact_date", missing["reviews"][0]["decay_flag"])
        self.assertEqual(missing["reviews"][0]["artifact_age"], "unknown")

        invalid = analyze_decay(
            "The workflow is ready for public release.",
            """## Proof: invalid date
- evidence artifact: local screenshot
- artifact date: yesterday
- evidence strength: artifact-backed
- evidence type: screenshot
- scope supported: local demo
- freshness window: 30 days
""",
            review_date="2026-05-26",
        )
        self.assertIn("invalid_artifact_date", invalid["reviews"][0]["decay_flag"])
        self.assertEqual(invalid["reviews"][0]["artifact_age"], "unknown")

    def test_markdown_structures_are_skipped(self):
        text = """# Heading should be skipped

Real claim needs current proof.

```markdown
Code block says the system is production-ready.
```

| claim | proof |
| --- | --- |
| Table claim is proven. | old screenshot |

> Blockquote demo claim is certified.
"""
        claims = extract_claims(text)

        self.assertEqual([claim.text for claim in claims], ["Real claim needs current proof."])
        self.assertEqual(claims[0].line, 3)

    def test_render_markdown_review_only_has_boundary_note_and_no_rewrite(self):
        review = analyze_decay(CLAIMS, PROOF_NOTES, review_date="2026-05-26")
        markdown = render_markdown(review)

        self.assertIn("| source line | claim | evidence artifact | match basis | artifact age | freshness window | decay flag | risk flag | bounded wording | next verification step |", markdown)
        self.assertIn("## Boundary Note", markdown)
        self.assertNotIn("## Revised", markdown)


if __name__ == "__main__":
    unittest.main()
