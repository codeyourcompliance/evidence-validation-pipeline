# Screenshot Evidence Gap

A screenshot is a view.

It is not the system state.

Screenshots may support audit narratives, reviewer understanding, and UI context. They should not silently replace source-bound, timestamped, integrity-checked evidence.

## Scope

This document is part of the CodeYourCompliance `evidence-validation-pipeline` repository.

It is a MAS TRM-inspired engineering artifact. It is not legal, regulatory, audit, or certification advice.

The examples are synthetic and illustrative.

## Evidence Admissibility Tiers

| Tier | Artifact type | Can support policy evaluation? | Example |
| --- | --- | --- | --- |
| Primary machine-verifiable evidence | Source-bound system evidence | Yes | API response, config export, runtime certificate metadata |
| Supporting artifact | Human-readable context | Sometimes, but usually not alone | Screenshot, UI capture, dashboard image |
| Manual claim | Human or vendor assertion | No, unless independently verified | Email confirmation, meeting note, vendor statement |
| Invalid evidence | Unreliable or unverifiable artifact | No | Hash mismatch, missing source, stale export, edited image |

## Screenshot Classification Test

Before a screenshot is used in an audit narrative, classify its role:

| Question | Why it matters |
| --- | --- |
| What system produced the screen? | A screenshot without source context is weak evidence. |
| When was the underlying data observed? | Capture time is not always observation time. |
| Was the page refreshed or generated from cached data? | A stale view can misrepresent system state. |
| Who captured it? | Reviewer context may matter for narrative use. |
| Was it edited or transformed? | Modified images should not become primary proof objects. |
| Is there a machine-verifiable source object? | Screenshots should usually support the source object, not replace it. |
| Is there an integrity hash for the artifact? | Hashing can show later mutation, but not original truth. |

## Suggested Screenshot Metadata

A screenshot used as supporting evidence should preserve:

```json
{
  "artifact_type": "screenshot",
  "evidentiary_role": "supporting_artifact",
  "captured_at_utc": "2026-06-01T08:30:00Z",
  "captured_by": "reviewer-001",
  "source_system": "example-admin-console",
  "source_url_or_path": "https://example.internal/settings/tls",
  "related_primary_evidence_id": "evd-tls-apache-001",
  "artifact_hash": "sha256:PLACEHOLDER",
  "classification": "supporting_artifact"
}
```

## Outcome Labels

Use explicit outcome labels before policy evaluation:

- `primary_evidence`
- `supporting_artifact`
- `manual_claim_only`
- `not_machine_verifiable`
- `invalid_evidence`
- `stale_artifact`

The label matters because reports can launder weak artifacts into apparent proof.

## Boundary Statement

A screenshot may explain the finding.

The primary evidence should support the proof.

This document does not claim screenshots are useless.

It claims their evidentiary role must be classified before they are used in reporting or policy evaluation.
