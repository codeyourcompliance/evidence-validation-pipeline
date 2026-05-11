# Week 3: Evidence Before Reporting

A report is downstream.

It cannot rescue stale evidence. It cannot repair a missing timestamp. It cannot prove that a configuration remained unchanged after collection.

This note records the Week 3 repository boundary for CodeYourCompliance: compliance automation starts at evidence, not reporting.

## Position

Compliance automation is not report automation.

Report automation makes audit packs faster. Evidence automation makes control claims harder to fake, harder to mutate, and easier to replay.

That is the useful distinction.

Reports persuade. Evidence survives.

## Audit Boundary

The evidence path must stay separate from the remediation path.

```text
System State
  -> Read-only Collection
  -> Timestamped Evidence
  -> Hash Seal
  -> Integrity Verification
  -> OPA Evaluation
  -> Audit Narrative
```

The audit boundary starts before the report.

Collection observes the system. It should not correct the system. If collection changes the target, the failed state may disappear before it is recorded.

Read-only collection is not a tooling preference. It is restraint.

## Minimal Evidence Object

A useful evidence object should preserve:

- what was observed
- when it was observed
- where it came from
- how it was collected
- who or what collected it
- whether it changed after collection
- which control expectation it supports
- which policy evaluation consumed it

Without those fields, data is not evidence. It is material for a report.

See [`../examples/minimal_evidence_object.json`](../examples/minimal_evidence_object.json).

## Integrity Before Policy

A hash does not prove compliance.

It proves whether the evidence changed after collection.

That narrow claim matters. It creates a trust boundary for the rest of the pipeline.

If integrity verification fails, policy evaluation should stop. OPA should not evaluate evidence that has already failed its own trust boundary.

The correct status is:

```text
invalid_evidence
```

Not:

```text
pass
fail
```

Bad evidence should not produce a clean result.

See [`../examples/invalid_evidence_result.json`](../examples/invalid_evidence_result.json).

## OPA Boundary

OPA is not the audit system.

It is a policy evaluator.

It should not collect evidence. It should not repair systems. It should not write the audit narrative.

Its job is narrow: take verified evidence and decide whether the observed state violates a defined control condition.

That narrowness keeps policy deterministic. Narrative can come later.

## TLS Example

Take an Apache HTTPS service.

The weak audit asks whether SSL is enabled.

The stronger audit asks when the certificate was observed, when it expires, which signature algorithm was used, whether the evidence was sealed, and whether that sealed evidence was verified before policy evaluation.

The first question checks a claim.

The second checks proof.

A certificate expiring within 48 hours is not a cosmetic issue. It is a control weakness.

A defensible audit narrative should stay tied to evidence:

> Based on verified TLS evidence collected at a specific time, the service was operating with a certificate approaching expiry within the defined threshold. This weakens assurance over secure communications and does not align with MAS TRM-inspired expectations for maintaining effective cryptographic controls.

No legal conclusion. No remediation theatre. Just evidence, expectation, and judgment.

## MAS TRM-Inspired Scope

MAS TRM is the context here, not legal advice.

MAS TRM-inspired means engineering interpretation. It does not mean MAS approval, certified compliance, legal advice, regulatory advice, audit sufficiency, or certification advice.

This repository does not claim that MAS TRM prescribes Ansible, SHA256, Python, OPA, Rego, JSON schemas, or any specific implementation pattern.

The purpose is narrower: to explore how technical compliance evidence can be collected, timestamped, sealed, verified, evaluated, and replayed.

## CodeYourCompliance Origin

This document is part of the CodeYourCompliance public technical work.

- Website: https://www.codeyourcompliance.com
- GitHub organization: https://github.com/codeyourcompliance
- Repository: https://github.com/codeyourcompliance/evidence-validation-pipeline

If you reference, fork, adapt, or discuss this material, preserve attribution to CodeYourCompliance and link back to the original repository.
