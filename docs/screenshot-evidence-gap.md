# Screenshot Evidence Gap Checklist

This checklist is a public CodeYourCompliance artifact.

It supports the article **A Screenshot Is a Supporting Artifact, Not a Proof Object**.

A screenshot can help explain audit evidence.

It should not silently replace source-bound, timestamped, integrity-checked evidence.

## Scope

This checklist focuses on the audit role of screenshots, UI captures, dashboard images, and manually captured visual artifacts.

It does not provide remediation advice.

It does not certify compliance.

It does not replace legal, regulatory, audit, certification, or compliance review.

MAS TRM-inspired means engineering interpretation, not regulatory advice.

## Core Boundary

A screenshot is a view.

It is not the system state.

A screenshot may show what an operator or reviewer saw at a point in time.

It does not automatically prove:

- when the underlying system state was observed
- which source system produced the data
- who or what collected it
- whether the page was refreshed
- whether the image changed after capture
- whether the policy result evaluated the same object

Screenshots are not useless.

Their role must be classified correctly.

## Evidence Admissibility Tiers

Use this table before treating a screenshot or related artifact as audit evidence.

| Tier | Artifact type | Can support policy evaluation? | Example |
|---|---|---|---|
| Primary machine-verifiable evidence | Source-bound system evidence | Yes | API response, config export, runtime certificate metadata |
| Supporting artifact | Human-readable context | Sometimes, but usually not alone | Screenshot, UI capture, dashboard image |
| Manual claim | Human or vendor assertion | No, unless independently verified | Email confirmation, meeting note, vendor statement |
| Invalid evidence | Unreliable or unverifiable artifact | No | Hash mismatch, missing source, stale export, edited image |

A screenshot usually belongs in the second tier.

It can explain the finding.

It should not become the finding.

## Screenshot Classification Test

Before using a screenshot in an audit pack, ask:

1. What role does this screenshot play?
2. Is it primary evidence or supporting context?
3. Does it have a capture timestamp?
4. Does it identify who or what captured it?
5. Does it identify the source system or source view?
6. Does it link to primary machine-verifiable evidence?
7. Does it have an integrity hash or other mutation check?
8. Was it captured before or after remediation?
9. Does the policy result reference this screenshot or a separate evidence object?
10. Can the same conclusion be reproduced without relying on the screenshot?

If these questions cannot be answered, the screenshot should not be treated as primary evidence.

## Suggested Screenshot Metadata

A screenshot used as a supporting artifact should preserve enough context to avoid ambiguity.

```yaml
artifact_id: string
artifact_type: supporting_artifact
screenshot_ref: string
captured_at: string
captured_by: string
source_system: string
source_view: string
related_control: string
linked_primary_evidence_ref: string
integrity:
  hash_algorithm: sha256
  hash_value: string
  sealed_at_utc: string
policy_result_ref: string
classification: supporting_artifact | not_machine_verifiable | invalid_evidence
```

This is not a final schema.

It is the minimum structure needed to reason about the role of a screenshot in an evidence package.

## Example: TLS Certificate Screenshot

For a checklist item such as `certificate valid`, a screenshot of a certificate page may show the expiry date.

That is not enough by itself.

The proof object should still include source-bound evidence fields.

```yaml
checklist_item: TLS certificate valid
primary_evidence:
  certificate_not_after: "2026-09-01T00:00:00Z"
  observed_at: "2026-05-25T10:31:00Z"
  source_system: "production-load-balancer"
  collector: "tls-cert-collector"
  collection_method: "runtime_observation"
  integrity_hash: "sha256:..."
  policy_result_ref: "policy-results/tls-cert-valid-2026-05-25.json"
supporting_artifact:
  screenshot_ref: "screenshots/tls-certificate-view.png"
  captured_at: "2026-05-25T10:35:00Z"
  captured_by: "reviewer-01"
  classification: supporting_artifact
```

The screenshot explains the finding.

The primary evidence supports the proof.

The policy result should bind to the primary evidence object.

## Outcome Labels

Use these labels when classifying screenshots and related artifacts:

```yaml
primary_evidence: Machine-verifiable evidence suitable for policy evaluation.
supporting_artifact: Human-readable context that supports the audit narrative.
manual_claim_only: Assertion without independent source-bound observation.
not_machine_verifiable: Artifact usable for human review but not automated evaluation.
invalid_evidence: Evidence integrity failed or cannot be verified.
stale_artifact: Artifact exists but is outside the expected freshness window.
```

## Failure Conditions

A screenshot should not be used as primary evidence when:

- it has no capture timestamp
- it has no source system context
- it has no collector or captured-by metadata
- it cannot be tied to primary evidence
- it was modified after capture without traceability
- it is outside the freshness window
- it conflicts with source-bound evidence
- it is only a vendor or human claim rendered as an image

When integrity fails, the correct state is not `fail`.

The correct state is `invalid_evidence`.

A failed control and invalid evidence are different audit states.

Do not mix them.

## Reporting Boundary

A report may include screenshots.

A report should not launder screenshots into proof.

A clean report built from weak artifacts is still weak.

Reports persuade.

Evidence survives.

## Suggested Use

Use this checklist before attaching screenshots to an audit pack.

Use it before mapping screenshots to MAS TRM-inspired evidence requirements.

Use it before treating UI captures, dashboards, or manually exported images as proof.

The checklist should answer one narrow question:

Is this screenshot primary evidence, supporting context, a manual claim, not machine-verifiable, or invalid evidence?

## Companion Article

Title: A Screenshot Is a Supporting Artifact, Not a Proof Object

Subtitle: Screenshots can help explain audit evidence. They should not replace it.

Companion artifact path:

`evidence-validation-pipeline/docs/screenshot-evidence-gap.md`

## Origin and Attribution

This artifact is published by CodeYourCompliance.

Website: https://www.codeyourcompliance.com

GitHub: https://github.com/codeyourcompliance

Forks, references, adaptations, and discussions should preserve attribution to CodeYourCompliance.

## Scope Boundary

MAS TRM-inspired means engineering interpretation.

This material is not legal, regulatory, audit, certification, compliance, or implementation advice.

A screenshot is a supporting artifact.

Evidence is proof material.
