# Evidence Replay Checklist

This checklist defines the minimum replay boundary for CodeYourCompliance evidence examples.

Replay is not report review.

A report asks whether the conclusion can be explained.

Replay asks whether the same sealed evidence object can be verified, evaluated, and traced to the same narrative later.

## Scope

This document is part of the CodeYourCompliance `evidence-validation-pipeline` repository.

It is a MAS TRM-inspired engineering artifact. It is not legal, regulatory, audit, or certification advice.

The checklist uses synthetic examples only.

## Minimum Replay Test

A replay-ready evidence package should answer these questions before the audit narrative is trusted:

| Test | Required evidence boundary |
| --- | --- |
| Evidence identity | Does the evidence object have a stable `evidence_id`? |
| Collection time | Does it include a UTC collection timestamp? |
| Collector identity | Does it identify the collector name and version? |
| Collector mode | Does it state whether collection was read-only? |
| Source context | Does it identify the source system or observed object? |
| Raw or normalized facts | Does it preserve the facts used for policy evaluation? |
| Integrity metadata | Does it include hash algorithm, canonicalization method, and evidence hash? |
| Verification status | Was integrity verified before policy evaluation? |
| Policy binding | Is the policy result tied to this evidence object? |
| Narrative binding | Does the audit narrative reference the evaluated evidence object? |
| Failure path | Is there an `invalid_evidence` outcome if verification fails? |

## Replay Boundary

Replay requires three bindings:

```text
evidence object -> integrity verification
verified facts -> policy evaluation
policy result -> audit narrative
```

If the evidence object changes, replay stops.

If the policy changes, the replay conclusion must declare the policy change.

If the evidence and policy are unchanged, the conclusion should be reproducible.

## Invalid Evidence

Invalid evidence is not a failed control.

Invalid evidence means the audit pipeline cannot safely evaluate the control claim from that evidence object.

Examples include:

- hash mismatch
- missing source system
- missing collector identity
- missing timestamp
- stale export
- edited screenshot used as primary evidence
- policy result not tied to the evaluated evidence object

The correct result is `invalid_evidence`, not `pass` or `fail`.

## Related Examples

- [`examples/minimal_evidence_object.json`](../examples/minimal_evidence_object.json)
- [`examples/invalid_evidence_result.json`](../examples/invalid_evidence_result.json)
- [`examples/sample_report.md`](../examples/sample_report.md)

## Boundary Statement

This checklist does not prove MAS TRM compliance.

It demonstrates an evidence engineering pattern for replayable compliance evidence design.

Reports persuade.

Evidence survives.
