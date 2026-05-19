# Evidence Replay Checklist

This checklist is a public CodeYourCompliance artifact.

It tests whether an audit evidence object can survive replay.

An audit pack may look complete and still fail as evidence. The question is not whether the report is readable. The question is whether the underlying evidence can be verified, evaluated, and replayed later.

## Scope

This checklist focuses on evidence readiness and replayability.

It does not provide remediation advice.

It does not certify compliance.

It does not replace legal, regulatory, audit, or certification review.

MAS TRM-inspired means engineering interpretation, not regulatory advice.

## Replay Principle

A replayable evidence object should be:

- timestamped
- source-bound
- collector-identified
- integrity-sealed
- verified before evaluation
- linked to a specific policy result
- capable of being re-evaluated later

If these properties are missing, the evidence may still be documentation. It is not strong machine-verifiable evidence.

## Minimum Replay Test

Take one evidence object from an audit pack.

Ask:

1. Does the evidence object include a collection timestamp?
2. Does it identify the collector?
3. Does it preserve source system context?
4. Does it preserve raw evidence before interpretation?
5. Is there an integrity hash or cryptographic seal?
6. Was integrity verified before policy evaluation?
7. Is the policy result tied to this specific evidence object?
8. Is there a defined `invalid_evidence` path?
9. Can the same evidence object be re-evaluated later?
10. Can the audit narrative point back to the verified evidence object?

## Evidence Object Readiness

A minimal replay-ready evidence object should include:

```yaml
evidence_id: string
collection_timestamp_utc: string
collector:
  name: string
  version: string
source_system:
  system_id: string
  environment: string
  evidence_type: string
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
  result: pass | fail | invalid_evidence
  evaluated_at_utc: string
audit_narrative_ref: string
```

This is not a final schema. It is the minimum structure needed to reason about replayability.

## Failure Conditions

Replay should stop before policy evaluation when evidence integrity fails.

The correct result is not `non_compliant`.

The correct result is `invalid_evidence`.

A failed control says the system may not meet the expected condition.

Invalid evidence says the audit cannot safely evaluate the system at all.

Do not mix these outcomes.

## Decision Boundary

Use this checklist only to decide whether evidence is ready for replay.

Do not use it to decide how to fix the underlying system.

Observation is not remediation.

Evidence is not a report.

A control is not proof.

The audit problem starts earlier.

## Outcome Labels

Use the following labels when testing an evidence object:

```yaml
replay_ready: Evidence includes enough structure to be verified and re-evaluated.
replay_incomplete: Evidence is missing one or more replay properties.
invalid_evidence: Evidence integrity failed or cannot be verified.
not_machine_verifiable: Evidence may support human review but cannot support machine evaluation.
```

## Suggested Use

Use this checklist before writing an audit narrative.

Use it before OPA policy evaluation.

Use it before treating exported reports, screenshots, or manually collected files as compliance evidence.

The checklist should answer one narrow question:

Can this evidence object survive replay?

## Companion Article

Title: Can Your Audit Evidence Survive Replay?

Subtitle: A short test for timestamped, sealed, and policy-evaluable compliance evidence.

## Origin and Attribution

This artifact is published by CodeYourCompliance.

Website: https://www.codeyourcompliance.com

GitHub: https://github.com/codeyourcompliance

Forks, references, adaptations, and discussions should preserve attribution to CodeYourCompliance.

## Scope Boundary

MAS TRM-inspired means engineering interpretation.

This material is not legal, regulatory, audit, certification, or compliance advice.

Reports persuade. Evidence survives.
