# Proof Decay Review

Review date: `2026-05-26`

## Review Table

| source line | claim | evidence artifact | match basis | artifact age | freshness window | decay flag | risk flag | bounded wording | next verification step |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3 | The workflow is validated for regulated use. | local regulated-use demo output; date: 2025-08-20; age: 279 days; scope: local demo with synthetic regulated-use data | keyword_match | 279 days | 30 days | proof_decay, stale_artifact, changed_conditions, limited_artifact | proofwashing, scope_mismatch, proof_language, uncorroborated | The local demo with synthetic regulated-use data was documented on 2025-08-20. This does not establish the current broader claim. | Run a current check and record fresh evidence before reusing this claim. |
| 5 | The checklist proves the workflow is compliant for financial review. | internal financial review checklist; date: 2025-09-01; age: 267 days; scope: internal checklist completed against a demo environment | keyword_match | 267 days | 14 days | proof_decay, stale_artifact, changed_conditions, limited_artifact | proofwashing, scope_mismatch, proof_language, uncorroborated | The internal checklist completed against a demo environment was documented on 2025-09-01. This does not establish current legal or financial reliability. | Run a current check and record fresh evidence before reusing this claim. |

## Boundary Note

This review uses local heuristics. It can surface stale or condition-shifted evidence, but it does not prove that a claim is true or false.
