import re
from dataclasses import dataclass
from datetime import date
from typing import Dict, Iterable, List, Optional, Set


EVIDENCE_STRENGTHS = {
    "unsupported",
    "self-attested",
    "artifact-backed",
    "externally corroborated",
    "live-demonstrable",
}

HIGH_STAKES_TERMS = {
    "approved",
    "certified",
    "clinical",
    "compliant",
    "compliance",
    "deployment",
    "enterprise",
    "financial",
    "hospital",
    "hospitals",
    "legal",
    "medical",
    "patient",
    "production",
    "ready",
    "regulated",
    "safe",
    "safety",
    "teams",
    "validated",
}

PROOF_TERMS = {
    "certified",
    "confirmed",
    "prove",
    "proved",
    "proven",
    "proves",
    "validated",
    "verified",
}

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "our",
    "the",
    "this",
    "to",
    "we",
    "with",
}


@dataclass
class Claim:
    text: str
    line: int


@dataclass
class ProofNote:
    label: str
    artifact: str
    artifact_date: Optional[date]
    strength: str
    artifact_date_status: str = "valid"
    evidence_type: str = ""
    scope_supported: str = ""
    freshness_window_days: int = 30
    changed_conditions: str = ""
    limitations: str = ""
    corroboration_status: str = ""

    @property
    def tokens(self) -> Set[str]:
        return _tokens(
            " ".join(
                [
                    self.label,
                    self.artifact,
                    self.evidence_type,
                    self.scope_supported,
                    self.changed_conditions,
                    self.limitations,
                ]
            )
        )

    def age_days(self, review_date: date) -> int:
        if self.artifact_date is None:
            return 0
        return max((review_date - self.artifact_date).days, 0)

    def summary(self, review_date: date) -> str:
        date_text = self.artifact_date.isoformat() if self.artifact_date else self.artifact_date_status
        age_text = f"{self.age_days(review_date)} days" if self.artifact_date else "unknown"
        return (
            f"{self.artifact or self.label}; date: {date_text}; "
            f"age: {age_text}; scope: {self.scope_supported or 'not stated'}"
        )


def analyze_decay(claims_text: str, proof_text: str = "", review_date: Optional[str] = None) -> Dict[str, object]:
    current_date = _parse_date(review_date) if review_date else date.today()
    claims = extract_claims(claims_text)
    proof_notes = parse_proof_notes(proof_text)
    reviews = []

    for index, claim in enumerate(claims):
        proof = match_proof(claim.text, proof_notes)
        match_basis = "keyword_match" if proof else "none"
        if proof is None and index < len(proof_notes):
            proof = proof_notes[index]
            match_basis = "ordered_fallback"
        decay_flags = classify_decay(proof, current_date)
        if match_basis == "ordered_fallback":
            decay_flags = _dedupe(decay_flags + ["low_confidence_match"])
        risk_flags = classify_risk(claim.text, proof, decay_flags)
        reviews.append(
            {
                "claim_line": claim.line,
                "claim": claim.text,
                "evidence_artifact": proof.summary(current_date) if proof else "No matching proof note found.",
                "match_basis": match_basis,
                "artifact_age": f"{proof.age_days(current_date)} days" if proof and proof.artifact_date else "unknown",
                "freshness_window": f"{proof.freshness_window_days} days" if proof else "not stated",
                "decay_flag": ", ".join(decay_flags) if decay_flags else "none",
                "risk_flag": ", ".join(risk_flags) if risk_flags else "none",
                "bounded_wording": suggest_bounded_wording(claim.text, proof, decay_flags),
                "next_verification_step": next_verification_step(proof, decay_flags, risk_flags),
            }
        )

    return {
        "review_date": current_date.isoformat(),
        "claims": claims,
        "proof_notes": proof_notes,
        "reviews": reviews,
    }


def extract_claims(text: str) -> List[Claim]:
    claims: List[Claim] = []
    in_fence = False
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence or _skip_markdown_line(stripped):
            continue
        content = re.sub(r"^[-*]\s+", "", stripped)
        for sentence in _split_sentences(content):
            if _looks_like_claim(sentence):
                claims.append(Claim(sentence, line_number))
    return claims


def parse_proof_notes(text: str) -> List[ProofNote]:
    notes: List[ProofNote] = []
    current: Optional[Dict[str, str]] = None

    def flush() -> None:
        nonlocal current
        if not current:
            return
        notes.append(_structured_note(current))
        current = None

    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.lower().startswith("## proof:"):
            flush()
            current = {"label": stripped.split(":", 1)[1].strip()}
            continue
        if current is None:
            continue
        field_line = re.sub(r"^[-*]\s+", "", stripped)
        if ":" in field_line:
            key, value = field_line.split(":", 1)
            current[_field_key(key)] = value.strip()
    flush()
    return notes


def match_proof(claim: str, proof_notes: Iterable[ProofNote]) -> Optional[ProofNote]:
    claim_tokens = _tokens(claim)
    best_note = None
    best_score = 0.0
    for note in proof_notes:
        score = (
            3.0 * len(claim_tokens & _tokens(note.label))
            + 2.0 * len(claim_tokens & _tokens(note.scope_supported))
            + 0.5 * len(claim_tokens & note.tokens)
        )
        if score > best_score:
            best_note = note
            best_score = score
    return best_note if best_score >= 1.0 else None


def classify_decay(proof: Optional[ProofNote], review_date: date) -> List[str]:
    if proof is None:
        return ["missing_current_proof"]
    flags: List[str] = []
    if proof.artifact_date_status != "valid":
        flags.append(proof.artifact_date_status)
    if proof.artifact_date and proof.age_days(review_date) > proof.freshness_window_days:
        flags.extend(["proof_decay", "stale_artifact"])
    if proof.changed_conditions:
        flags.append("changed_conditions")
    if proof.strength in {"unsupported", "self-attested"}:
        flags.append("weak_proof")
    if proof.strength == "artifact-backed" and _proof_is_limited(proof):
        flags.append("limited_artifact")
    return _dedupe(flags)


def classify_risk(claim: str, proof: Optional[ProofNote], decay_flags: List[str]) -> List[str]:
    lower = claim.lower()
    risks: List[str] = []
    if decay_flags and decay_flags != ["missing_current_proof"]:
        risks.append("proofwashing")
    if "missing_current_proof" in decay_flags:
        risks.append("evidence_gap")
    if "low_confidence_match" in decay_flags:
        risks.append("low_confidence_match")
    if _contains_term(lower, HIGH_STAKES_TERMS):
        risks.append("scope_mismatch")
    if _contains_term(lower, PROOF_TERMS):
        risks.append("proof_language")
    if any(term in lower for term in ("medical", "clinical", "hospital", "patient", "safe", "safety")):
        risks.append("medical_or_clinical_safety")
    if proof and proof.corroboration_status.lower() in {"none", "not corroborated", "uncorroborated"}:
        risks.append("uncorroborated")
    return _dedupe(risks)


def suggest_bounded_wording(claim: str, proof: Optional[ProofNote], decay_flags: List[str]) -> str:
    unsupported_scope = _unsupported_scope(claim)
    if proof:
        scope = proof.scope_supported or "the narrower artifact scope"
        artifact_date = proof.artifact_date.isoformat() if proof.artifact_date else proof.artifact_date_status.replace("_", " ")
        current_scope = _current_scope_phrase(unsupported_scope)
        return (
            f"{_sentence_from_scope(scope)} was documented on {artifact_date}. "
            f"This does not establish {current_scope}."
        )
    return f"Treat this as unsupported until current proof is added: {claim.rstrip('.')}."


def next_verification_step(proof: Optional[ProofNote], decay_flags: List[str], risk_flags: List[str]) -> str:
    if proof is None:
        return "Add current proof notes or narrow the claim."
    if "low_confidence_match" in decay_flags:
        return "Verify that the matched proof note belongs to this claim before using it."
    if "missing_artifact_date" in decay_flags or "invalid_artifact_date" in decay_flags:
        return "Add a valid artifact date before relying on this proof note."
    if "stale_artifact" in decay_flags or "changed_conditions" in decay_flags:
        return "Run a current check and record fresh evidence before reusing this claim."
    if "scope_mismatch" in risk_flags:
        return "Add proof for the broader scope or keep the claim within the artifact scope."
    return "Keep the proof date and scope visible when publishing the claim."


def render_markdown(review: Dict[str, object]) -> str:
    rows = [
        "# Proof Decay Review",
        "",
        f"Review date: `{review['review_date']}`",
        "",
        "## Review Table",
        "",
        "| source line | claim | evidence artifact | match basis | artifact age | freshness window | decay flag | risk flag | bounded wording | next verification step |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    for item in review["reviews"]:
        rows.append(
            "| "
            + " | ".join(
                _escape_table(str(item[key]))
                for key in (
                    "claim_line",
                    "claim",
                    "evidence_artifact",
                    "match_basis",
                    "artifact_age",
                    "freshness_window",
                    "decay_flag",
                    "risk_flag",
                    "bounded_wording",
                    "next_verification_step",
                )
            )
            + " |"
        )

    rows.extend(
        [
            "",
            "## Boundary Note",
            "",
            "This review uses local heuristics. It can surface stale or condition-shifted evidence, but it does not prove that a claim is true or false.",
            "",
        ]
    )
    return "\n".join(rows)


def _structured_note(fields: Dict[str, str]) -> ProofNote:
    strength = fields.get("evidence_strength", fields.get("strength", "self-attested")).lower()
    artifact_date, artifact_date_status = _parse_optional_date(fields.get("artifact_date", ""))
    return ProofNote(
        label=fields.get("label", ""),
        artifact=fields.get("evidence_artifact", fields.get("artifact", fields.get("label", ""))),
        artifact_date=artifact_date,
        strength=strength if strength in EVIDENCE_STRENGTHS else "self-attested",
        artifact_date_status=artifact_date_status,
        evidence_type=fields.get("evidence_type", ""),
        scope_supported=fields.get("scope_supported", ""),
        freshness_window_days=_parse_days(fields.get("freshness_window", "30 days")),
        changed_conditions=fields.get("changed_conditions", ""),
        limitations=fields.get("limitations", ""),
        corroboration_status=fields.get("corroboration_status", ""),
    )


def _skip_markdown_line(stripped: str) -> bool:
    if not stripped:
        return True
    if re.match(r"^#{1,6}\s+", stripped):
        return True
    if stripped.startswith("|") or stripped.startswith(">"):
        return True
    field_line = re.sub(r"^[-*]\s+", "", stripped).lower()
    return field_line.startswith(
        (
            "artifact date:",
            "changed conditions:",
            "corroboration status:",
            "evidence artifact:",
            "evidence strength:",
            "evidence type:",
            "freshness window:",
            "limitations:",
            "scope supported:",
        )
    )


def _looks_like_claim(sentence: str) -> bool:
    return len(sentence.split()) >= 4 and bool(re.search(r"[A-Za-z]", sentence))


def _split_sentences(text: str) -> List[str]:
    return [piece.strip() for piece in re.split(r"(?<=[.!?])\s+", text) if piece.strip()]


def _tokens(text: str) -> Set[str]:
    return {
        _token_root(token)
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 2 and token not in STOPWORDS
    }


def _token_root(token: str) -> str:
    if len(token) > 4 and token.endswith("s"):
        return token[:-1]
    return token


def _contains_term(text: str, terms: Set[str]) -> bool:
    return any(re.search(rf"\b{re.escape(term)}\b", text) for term in terms)


def _parse_date(value: str) -> date:
    return date.fromisoformat(value.strip())


def _parse_optional_date(value: str) -> tuple[Optional[date], str]:
    stripped = value.strip()
    if not stripped:
        return None, "missing_artifact_date"
    try:
        return date.fromisoformat(stripped), "valid"
    except ValueError:
        return None, "invalid_artifact_date"


def _parse_days(value: str) -> int:
    match = re.search(r"\d+", value)
    return int(match.group(0)) if match else 30


def _proof_is_limited(proof: ProofNote) -> bool:
    combined = " ".join(
        [
            proof.evidence_type,
            proof.scope_supported,
            proof.changed_conditions,
            proof.limitations,
            proof.corroboration_status,
        ]
    ).lower()
    return any(term in combined for term in ("local", "demo", "sample", "none", "no external", "no production", "checklist"))


def _unsupported_scope(claim: str) -> str:
    lower = claim.lower()
    if any(term in lower for term in ("medical", "clinical", "hospital", "patient", "safe", "safety")):
        return "medical or clinical safety"
    if "financial" in lower or "legal" in lower or "compliant" in lower or "compliance" in lower:
        return "legal or financial reliability"
    if "production" in lower or "release" in lower or "deployment" in lower or "ready" in lower:
        return "release readiness"
    if "enterprise" in lower or "teams" in lower:
        return "enterprise or organization-wide readiness"
    return "the broader claim"


def _current_scope_phrase(scope: str) -> str:
    if scope.startswith("the "):
        return f"the current {scope[4:]}"
    return f"current {scope}"


def _sentence_from_scope(scope: str) -> str:
    stripped = scope.strip().rstrip(".")
    if not stripped:
        return "The narrower evidence scope"
    first_word = stripped.split()[0].lower()
    if first_word in {"internal", "local"}:
        return f"The {stripped}"
    if first_word in {"one", "the", "this", "that", "these", "those"}:
        return stripped[0].upper() + stripped[1:]
    article = "An" if stripped[:1].lower() in {"a", "e", "i", "o", "u"} else "A"
    return f"{article} {stripped}"


def _escape_table(value: str) -> str:
    return value.replace("\n", " ").replace("|", "\\|")


def _field_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _dedupe(values: List[str]) -> List[str]:
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
