# Evidence Replay Checklist

This checklist is a public CodeYourCompliance artifact.

It supports the article **What a MAS TRM Checklist Cannot Prove**.

A checklist can organize compliance work. It can track owners, status, attached files, and review progress.

It cannot prove that a control was true at a specific point in time.

That proof requires replayable, timestamped, source-bound, and integrity-checked evidence.

## Scope

This checklist focuses on evidence readiness and replayability.

It does not provide remediation advice.

It does not certify compliance.

It does not replace legal, regulatory, audit, certification, or compliance review.

MAS TRM-inspired means engineering interpretation, not regulatory advice.

## Core Boundary

Do not collapse these objects into one row.

| Object | Function | What it cannot do alone |
|---|---|---|
| Checklist | Intake and work tracking | Prove system state |
| Control | Expected condition or requirement | Prove the condition was true |
| Evidence | Proof material collected from a source | Explain the full audit narrative |
| Policy result | Evaluation outcome from verified evidence | Repair invalid or missing evidence |
| Report | Narrative for review | Replace the evidence object |

Checklist is intake.

Evidence is proof material.

Report is narrative.

Proof requires a chain between them.

## Replay Principle

A replayable evidence object should be:

- timestamped
- source-bound
- collector-identified
- collection-method explicit
- integrity-sealed
- verified before evaluation
- linked to a specific policy result
- capable of being re-evaluated later

If these properties are missing, the evidence may still be documentation. It is not strong machine-verifiable evidence.

## Checklist Row to Evidence Requirement

A checklist row should map to an evidence requirement.

The checklist row should not be treated as the evidence itself.

| Checklist item | What it claims | What it cannot prove | Minimum evidence fields |
|---|---|---|---|
| TLS enabled | TLS is configured | When and where TLS state was observed | `observed_at`, `source_system`, `collector` |
| Certificate valid | Certificate was valid | Whether validity came from runtime state or human claim | `certificate_not_after`, `collection_method` |
| Logging enabled | Logs are enabled | Whether logs were actually generated and retained | `log_source`, `sample_window` |
| Access reviewed | User access was reviewed | Whether the user list came from the authoritative source | `identity_source`, `exported_at` |
| Vendor control confirmed | Vendor control exists | Whether this is evidence or only a vendor statement | `evidence_type`, `attestation_date` |

The fourth column is the work.

A checklist without evidence requirements is a tracking sheet.

It is not proof material.

## Minimum Replay Test

Take one evidence object from an audit pack.

Ask:

1. Does the evidence object include a collection timestamp?
2. Does it identify the collector?
3. Does it identify the source system?
4. Does it state the collection method?
5. Does it preserve raw evidence before interpretation?
6. Is there an integrity hash or cryptographic seal?
7. Was integrity verified before policy evaluation?
8. Is the policy result tied to this specific evidence object?
9. Is there a defined `invalid_evidence` path?
10. Can the same evidence object be re-evaluated later?
11. Can the audit narrative point back to the verified evidence object?
12. Can the evidence freshness window be assessed?

If the answer is unclear, the evidence is not replay-ready.

## Evidence Object Readiness

A minimal replay-ready evidence object should include:

```yaml
evidence_id: string
observed_at: string
source_system:
  system_id: string
  environment: string
  evidence_type: string
collector:
  name: string
  version: string
collection_method:
  type: runtime_observation | api_pull | file_export | human_attestation | other
  read_only: true | false
raw_evidence_ref: string
integrity:
  hash_algorithm: sha256
  hash_value: string
  sealed_at_utc: string
verification:
  status: verified | invalid_evidence | not_verified
  verified_at_utc: string
policy_evaluation:
  engine: opa
  policy_id: string
  policy_version: string
  policy_result_ref: string
  result: pass | fail | invalid_evidence
  evaluated_at_utc: string
freshness:
  valid_until_utc: string
  freshness_window: string
audit_narrative_ref: string
```

This is not a final schema.

It is the minimum structure needed to reason about replayability.

## Example Evidence Requirement: TLS Certificate Valid

For a checklist item such as `TLS certificate valid`, the evidence requirement should include:

```yaml
checklist_item: TLS certificate valid
evidence_requirement:
  required_fields:
    - certificate_not_after
    - observed_at
    - source_system
    - collector
    - collection_method
    - integrity_hash
    - policy_result_ref
  required_properties:
    runtime_observation: true
    integrity_verification_before_policy: true
    policy_result_bound_to_evidence: true
```

The purpose is narrow.

It proves whether the policy result can be traced back to the same evidence object that was collected.

It does not prove that the whole environment is compliant.

## Failure Conditions

Replay should stop before policy evaluation when evidence integrity fails.

The correct result is not `non_compliant`.

The correct result is `invalid_evidence`.

A failed control and invalid evidence are different audit states.

A failed control means the evidence was usable and the observed state did not satisfy the policy.

Invalid evidence means the evidence itself cannot be relied upon.

Invalid evidence may occur when:

- the integrity hash does not match
- the source system is missing or unclear
- the collector is unknown
- the collection method is not declared
- the evidence was modified after collection
- the evidence is outside the freshness window
- the policy result does not reference the same evidence object
- the evidence came from a human claim when runtime observation was required

Do not mix these outcomes.

## Observation vs Remediation

Observation records what was seen.

Remediation records what was changed.

Policy evaluation records whether the observed state satisfies the rule.

Narrative explains the sequence.

These should be separate evidence objects or separately referenced events.

If a checklist row becomes green after remediation, the replay pack should still preserve:

- original observation
- remediation action reference
- post-remediation observation
- policy evaluation result
- audit narrative reference

If the collector changes the system, the evidence has already lost part of its value.

Read-only collection is not elegance.

It is restraint.

## Outcome Labels

Use the following labels when testing an evidence object:

```yaml
replay_ready: Evidence includes enough structure to be verified and re-evaluated.
replay_incomplete: Evidence is missing one or more replay properties.
invalid_evidence: Evidence integrity failed or cannot be verified.
not_machine_verifiable: Evidence may support human review but cannot support machine evaluation.
manual_claim_only: Evidence is a human assertion without source-bound observation.
stale_evidence: Evidence exists but is outside the required freshness window.
```

## Suggested Use

Use this checklist before writing an audit narrative.

Use it before OPA policy evaluation.

Use it before treating exported reports, screenshots, or manually collected files as compliance evidence.

Use it when converting a MAS TRM checklist item into an evidence requirement.

The checklist should answer one narrow question:

Can this evidence object survive replay?

## Companion Article

Title: What a MAS TRM Checklist Cannot Prove

Subtitle: A checklist can organize audit readiness. It cannot prove system state.

Companion artifact path:

`evidence-validation-pipeline/docs/evidence-replay-checklist.md`

## Origin and Attribution

This artifact is published by CodeYourCompliance.

Website: https://www.codeyourcompliance.com

GitHub: https://github.com/codeyourcompliance

Forks, references, adaptations, and discussions should preserve attribution to CodeYourCompliance.

## Scope Boundary

MAS TRM-inspired means engineering interpretation.

This material is not legal, regulatory, audit, certification, compliance, or implementation advice.

Reports persuade. Evidence survives.
