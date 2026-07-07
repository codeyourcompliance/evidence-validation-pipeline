package evidence.freshness

# MAS TRM-inspired engineering example.
# This policy classifies evidence freshness before control evaluation.
# It is not legal, regulatory, audit, certification, compliance, or implementation advice.

default allow_policy_evaluation := false

freshness_status := status if {
  status := input.evidence_freshness.freshness_status
}

fresh_evidence if {
  freshness_status == "fresh"
}

stale_evidence if {
  freshness_status == "stale"
}

expired_evidence if {
  freshness_status == "expired"
}

unknown_freshness if {
  not input.evidence_freshness.freshness_status
}

allow_policy_evaluation if {
  input.integrity.verification_status == "verified"
  fresh_evidence
}

freshness_findings contains finding if {
  stale_evidence
  finding := {
    "code": "EVIDENCE_FRESHNESS_WINDOW_EXPIRED",
    "status": "stale_evidence",
    "message": "Evidence integrity verification passed, but the evidence is stale and should not support a current compliance conclusion."
  }
}

freshness_findings contains finding if {
  expired_evidence
  finding := {
    "code": "EVIDENCE_EXPIRED",
    "status": "expired_evidence",
    "message": "Evidence has expired and should not be used for current policy evaluation."
  }
}

freshness_findings contains finding if {
  unknown_freshness
  finding := {
    "code": "EVIDENCE_FRESHNESS_UNKNOWN",
    "status": "invalid_evidence",
    "message": "Evidence freshness status is missing. Policy evaluation should not proceed."
  }
}

freshness_findings contains finding if {
  input.integrity.verification_status != "verified"
  finding := {
    "code": "EVIDENCE_INTEGRITY_NOT_VERIFIED",
    "status": "invalid_evidence",
    "message": "Evidence integrity is not verified. Freshness cannot rescue invalid evidence."
  }
}

evaluation_boundary := boundary if {
  allow_policy_evaluation
  boundary := {
    "policy_evaluation_allowed": true,
    "status": "fresh_verified_evidence",
    "message": "Evidence is verified and fresh enough for downstream policy evaluation."
  }
}

evaluation_boundary := boundary if {
  not allow_policy_evaluation
  boundary := {
    "policy_evaluation_allowed": false,
    "status": "blocked_by_evidence_quality_gate",
    "findings": freshness_findings
  }
}
