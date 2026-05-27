# Proof Decay Review

Review date: `2026-05-26`

## Review Table

| source line | claim | evidence artifact | match basis | artifact age | freshness window | decay flag | risk flag | bounded wording | next verification step |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3 | The model is safe for hospitals. | local hospital safety checklist; date: 2025-09-15; age: 253 days; scope: local checklist against sample prompts | keyword_match | 253 days | 14 days | proof_decay, stale_artifact, changed_conditions, limited_artifact | proofwashing, scope_mismatch, medical_or_clinical_safety, uncorroborated | The local checklist against sample prompts was documented on 2025-09-15. This does not establish current medical or clinical safety. | Run a current check and record fresh evidence before reusing this claim. |
| 5 | The checklist proves this workflow is approved for patient-facing clinical use. | internal patient-facing clinical approval note draft; date: 2025-09-20; age: 248 days; scope: internal note with no approval evidence for patient-facing clinical use | keyword_match | 248 days | 14 days | proof_decay, stale_artifact, changed_conditions, weak_proof | proofwashing, scope_mismatch, proof_language, medical_or_clinical_safety, uncorroborated | The internal note with no approval evidence for patient-facing clinical use was documented on 2025-09-20. This does not establish current medical or clinical safety. | Run a current check and record fresh evidence before reusing this claim. |

## Boundary Note

This review uses local heuristics. It can surface stale or condition-shifted evidence, but it does not prove that a claim is true or false.
