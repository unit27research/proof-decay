# Proof Decay

[![CI](https://github.com/unit27research/proof-decay/actions/workflows/ci.yml/badge.svg)](https://github.com/unit27research/proof-decay/actions/workflows/ci.yml)

Old proof can keep working rhetorically after it stops working evidentially. Proof Decay is a small local instrument for reviewing whether stale or condition-shifted evidence is being reused to support current claims.

The category is stale-evidence review.

## Release Status

`SOURCE_STATUS: PUBLIC_PACKAGE`
`ACCESS_STATUS: CLEARED_FOR_EXTERNAL_USE`
`UNIT27_POSITION: ADJACENT_CLAIM_REVIEW_UTILITY`

This repository is a Unit27 public utility: visible, inspectable, and intended for orientation, testing, and practical use. Controlled protocol materials remain outside this source package.

It answers one narrow question:

> Is old proof being reused as if it still supports a current claim?

## Failure Mode

**Proof decay** is when evidence that may once have supported a narrower claim becomes stale because time passed, the system changed, the conditions changed, or the artifact was never broad enough for the current claim.

This is one way proofwashing happens: a screenshot, checklist, demo, eval run, or terminal result keeps getting cited after it no longer establishes what the claim now says.

## What Proof Decay Does

Proof Decay reads current claims and optional structured proof notes, then produces a review-only table.

It is designed to help surface:

- `proof_decay`
- `stale_artifact`
- `changed_conditions`
- `limited_artifact`
- possible `proofwashing`
- possible `scope_mismatch`
- bounded wording for manual review
- next verification steps

The working rule is simple: proof before claim, current proof before current claim.

## What It Does Not Do

Proof Decay is not a verifier, fact-checker, fraud detector, certification system, compliance system, legal reviewer, medical safety tool, or truth oracle.

It does not prove that a claim is true or false. It does not inspect external sources, validate screenshots, audit code, certify evidence, or decide what you should publish.

It is a heuristic review aid. The output is a prompt for human judgment, not a final authority.

## Where It Fits

Proof Decay sits beside Humility Engine and Claim Drift as an adjacent claim-review utility.

- Humility Engine asks: "Does this claim outrun its evidence?"
- Claim Drift asks: "Did this claim become stronger between drafts?"
- Proof Decay asks: "Is old proof being reused as current proof?"

It is also distinct from Proof Ledger. Proof Ledger records proof artifacts. Proof Decay reviews whether an artifact's age, freshness window, or changed conditions make it unsafe to reuse for a current claim.

## Who It Is For

- builders reviewing public claims before release
- researchers and operators preserving evidence boundaries over time
- teams checking whether old demos or evals still support current wording
- anyone trying to avoid turning stale artifacts into current proof

## Quick Demo

Run the synthetic portfolio scenario:

```bash
python3 run.py examples/scenarios/portfolio_claim.md \
  --proof examples/scenarios/portfolio_proof.md \
  --output examples/reviews/portfolio_decay_review.md \
  --review-date 2026-05-26 \
  --review-only
```

The output is a proof-decay table with source lines, match basis, artifact dates, artifact age, freshness windows, risk flags, bounded wording, and next verification steps.

## Before / After Example

Current claim:

> The workflow is ready for public release.

Proof available:

> Local demo screenshot from 2025-10-01. Code changed after the screenshot. No current CI run.

Proof Decay review result:

> A local demo on synthetic prompts was documented on 2025-10-01. This does not establish current release readiness.

## Synthetic Demo Scenarios

The repo includes three synthetic scenarios:

- `examples/scenarios/portfolio_claim.md`
- `examples/scenarios/org_readiness_claim.md`
- `examples/scenarios/medical_safety_claim.md`

Generated review-only outputs live in:

- `examples/reviews/portfolio_decay_review.md`
- `examples/reviews/org_readiness_decay_review.md`
- `examples/reviews/medical_safety_decay_review.md`

## Run Your Own Claims

Requirements: Python 3. No package install is required.

```bash
python3 run.py claims.md --proof proof_notes.md --output review.md --review-only
```

The tool does not rewrite the source file. Read the review table and revise manually.

## Structured Proof Notes

Proof notes use a small structured Markdown format:

```markdown
## Proof: local demo screenshot
- evidence artifact: local demo screenshot
- artifact date: 2025-10-01
- evidence strength: artifact-backed
- evidence type: screenshot
- scope supported: local demo on synthetic prompts
- freshness window: 30 days
- changed conditions: code changed after screenshot
- limitations: no production deployment; no external users
- corroboration status: none
```

Supported evidence-strength values:

- `unsupported`
- `self-attested`
- `artifact-backed`
- `externally corroborated`
- `live-demonstrable`

## Review Table Schema

| field | meaning |
| --- | --- |
| source line | Source line where the extracted claim starts. |
| claim | Current claim text. |
| evidence artifact | Best matching structured proof note. |
| match basis | Whether the proof note was matched by keyword or ordered fallback. |
| artifact age | Age of the artifact as of the review date. |
| freshness window | Declared useful life of the artifact. |
| decay flag | Staleness, changed-condition, weak-proof, or limited-artifact signal. |
| risk flag | Possible proofwashing, scope mismatch, high-stakes risk, or `none`. |
| bounded wording | Narrower claim language for manual review. |
| next verification step | What current evidence or wording change should happen next. |

## Current Limits

- Claim extraction is sentence-based and may miss claims spread across sections.
- Review-only output is the only supported output shape.
- Before/proof matching is keyword-based with an ordered fallback. Ordered fallback is marked as `low_confidence_match`.
- Date freshness depends on the artifact date and declared freshness window in the proof notes.
- Missing or invalid artifact dates are surfaced as review flags rather than treated as proof.
- The tool does not inspect files, URLs, screenshots, logs, demos, or external sources.
- Suggested bounded wording is for manual editing, not automatic source replacement.

## Reliability

CI verifies the unit tests, Python compile check, and three review-only demo runs before changes are considered ready.

## Verify

```bash
python3 -m unittest discover -s tests
PYTHONPYCACHEPREFIX=/private/tmp/proof_decay_pycache python3 -m py_compile proof_decay.py run.py
```

## License

MIT
