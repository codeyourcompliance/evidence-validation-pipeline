# Week 3: Evidence Before Reporting

The report is not the control.

The report is a downstream narrative derived from evidence.

Week 3 establishes the evidence-first audit boundary for the CodeYourCompliance `evidence-validation-pipeline` repository.

## Scope

This document is part of a MAS TRM-inspired engineering demonstration.

It is not legal, regulatory, audit, or certification advice.

The purpose is to show how a technical compliance finding can be derived from timestamped, integrity-checked, machine-evaluable evidence rather than from static screenshots, manual checklists, or after-the-fact reports.

## Minimum Evidence Object

A minimum evidence object should preserve:

- what was observed
- when it was observed
- where it came from
- how it was collected
- who or what collected it
- whether collection changed the target system
- whether the evidence changed after collection
- which control expectation it supports
- which policy evaluation consumed it
- which audit narrative references it

The companion example is:

- [`examples/minimal_evidence_object.json`](../examples/minimal_evidence_object.json)

## Required Boundary

Policy evaluation should consume verified evidence or verified derived facts.

It should not consume untrusted raw artifacts, manually attached files, or screenshots without classification.

```text
raw observation
-> normalized evidence object
-> integrity verification
-> derived facts
-> policy evaluation
-> audit narrative
```

The audit boundary starts before the report.

Bad evidence should not produce a clean result.

## Invalid Evidence Rule

If integrity verification fails, OPA should not run.

The correct result is `invalid_evidence`, not `pass` or `fail`.

The companion example is:

- [`examples/invalid_evidence_result.json`](../examples/invalid_evidence_result.json)

## Report Boundary

A report can explain a finding.

It cannot repair missing evidence.

It cannot create a timestamp after the fact.

It cannot prove that an artifact remained unchanged after collection.

It should point back to the evidence object and policy result that produced the conclusion.

The companion narrative example is:

- [`examples/sample_report.md`](../examples/sample_report.md)

## Boundary Statement

Evidence processing is upstream of reporting.

Reporting is not proof.

Where technical evidence exists, compliance conclusions should be replayable.
