# Evidence Validation Pipeline

![Shifting from Documentation to Replayable Evidence](assets/images/Shifting%20from%20Documentation%20to%20Replayable%20Evidence.png)

> A minimal MAS TRM-inspired evidence pipeline for evidence-first compliance automation.

This repository demonstrates a CodeYourCompliance technical pattern:

**Compliance automation should start with evidence, not reports.**

The goal is to show how a technical compliance finding can be derived from timestamped, integrity-checked, machine-evaluable evidence rather than from static screenshots, manual checklists, or after-the-fact reports.

This project is an architecture and demo asset. It is not legal, regulatory, audit, or certification advice.

## Project Origin and Attribution

This repository is part of **CodeYourCompliance**, a public technical project exploring MAS TRM-inspired compliance automation through replayable evidence, policy-as-code, and audit-ready evidence structures.

- Website: https://www.codeyourcompliance.com
- GitHub organization: https://github.com/codeyourcompliance
- Original repository: https://github.com/codeyourcompliance/evidence-validation-pipeline
- Companion article: https://www.codeyourcompliance.com/p/compliance-is-not-documentation-it-18e

This repository is the original public CodeYourCompliance implementation track for the `evidence-validation-pipeline` pattern.

If you reference, fork, adapt, or discuss this project, please preserve attribution to CodeYourCompliance and link back to the original repository.

## Boundary

MAS TRM-inspired means engineering interpretation. It does not mean MAS approval, certified compliance, legal advice, regulatory advice, or audit sufficiency.

This project does not claim that MAS TRM prescribes Ansible, SHA256, Python, OPA, Rego, JSON schemas, or any specific implementation pattern.

The purpose is narrower: to explore how technical compliance evidence can be collected, timestamped, sealed, verified, evaluated, and replayed.

## Position

A report is downstream.

It cannot rescue stale evidence. It cannot repair a missing timestamp. It cannot prove that a configuration remained unchanged after collection.

This repository treats compliance automation as an evidence pipeline, not a report generator.

The pipeline must make control claims harder to fake, harder to mutate, and easier to replay.

Reports persuade. Evidence survives.

## Purpose

The `evidence-validation-pipeline` project shows how to move from static audit narratives to replayable evidence workflows.

The minimal pipeline is:

1. Collect evidence from a target system in read-only mode.
2. Bind the evidence to a timestamp.
3. Generate an integrity hash for the evidence package.
4. Verify the evidence before policy evaluation.
5. Derive machine-readable facts.
6. Evaluate the facts with policy-as-code.
7. Generate a MAS TRM-inspired audit narrative.

The first demo scenario uses Apache HTTPD with TLS enabled. The target system is intentionally configured with a TLS certificate approaching expiry, such as within 48 hours, so the pipeline can produce a clear technical finding.

## Related Articles

This repository accompanies the CodeYourCompliance article series on MAS TRM-inspired compliance automation.

### Week 1

**Compliance Is Not Documentation. It Is Evidence That Can Be Replayed.**

Substack: https://www.codeyourcompliance.com/p/compliance-is-not-documentation-it-18e

The article introduces the core thesis behind this repository: compliance evidence should be collectible, timestamped, integrity-checked, machine-evaluable, and replayable.

### Week 2

**Read-Only Evidence Collection Is Not a Convenience. It Is an Audit Boundary.**

Substack: https://www.codeyourcompliance.com/p/read-only-collection-as-an-audit

The article explains why evidence collection should observe the target system without modifying it. Collection is evidence work. Remediation belongs in a separate workflow.

### Week 3

**Compliance Automation Starts at Evidence.**

Substack: https://www.codeyourcompliance.com/p/compliance-automation-starts-at-evidence

The Week 3 increment sharpens the repository boundary: report automation is not evidence automation. A clean audit pack can still be built on weak evidence. Policy evaluation should occur only after evidence is collected, timestamped, sealed, and verified.

## Content Relationship

- **Substack articles:** explain the problem language and architecture thesis.
- **This repository:** stores sample evidence structures, report examples, and implementation increments.
- **Week 2 increment:** adds the first read-only collection pattern.
- **Week 3 increment:** adds the evidence-first audit boundary, minimal evidence object, and invalid evidence result example.
- **Future releases:** will extend schema validation, integrity verification, and OPA/Rego policy examples.

## Architecture Overview

![Evidence Validation Pipeline](assets/images/Evidence%20Validation%20Pipeline.png)

In prose, the flow is simple:

System state is collected in read-only mode, packaged as timestamped evidence, sealed with an integrity hash, verified before policy evaluation, converted into derived facts, evaluated through policy logic, and finally translated into an audit narrative.

```text
System State
  -> Read-only Collection
  -> Timestamped Evidence
  -> Hash Seal
  -> Integrity Verification
  -> OPA Evaluation
  -> Audit Narrative
```

The audit boundary starts before the report. Bad evidence should not produce a clean result.

## Week 2 Increment: Read-Only Evidence Collection

Week 2 adds the first concrete read-only collection pattern.

The purpose of this increment is to separate observation from remediation. The collector is expected to gather system baseline evidence without installing packages, restarting services, rewriting configuration, or otherwise changing the target system.

The output evidence event should include:

- `host_id`
- `collector`
- `collector_version`
- `timestamp_utc`
- `evidence_type`
- `data`

This keeps the collector outside the system state being assessed.

Collection is evidence work. Remediation belongs in a separate workflow.

### Failure Observability Boundary

This increment also establishes the first failure observability boundary in the pipeline.

Read-only collection does not repair the system. It makes system state observable without moving it.

The first observable event is the evidence event: a timestamped record of system state collected without remediation. Policy evaluation and remediation should occur after this boundary, not inside it.

Detection before remediation.

## Week 3 Increment: Evidence Before Reporting

Week 3 adds the evidence-first audit boundary.

The report is not the control. The report is a downstream narrative derived from evidence.

The minimum evidence object should preserve:

- what was observed
- when it was observed
- where it came from
- how it was collected
- who or what collected it
- whether it changed after collection
- which control expectation it supports
- which policy evaluation consumed it

See [`examples/minimal_evidence_object.json`](examples/minimal_evidence_object.json).

This increment also fixes the pipeline rule:

If integrity verification fails, OPA should not run. The correct result is `invalid_evidence`, not `pass` or `fail`.

See [`examples/invalid_evidence_result.json`](examples/invalid_evidence_result.json).

## Components

### Read-only collection

Ansible is used as the collection mechanism. The collector should observe the target system without modifying it.

The first demo assumes:

- Rocky Linux 10 as the audit controller
- Rocky Linux 9 as the Apache HTTPD target
- Apache HTTPD with TLS enabled
- TLS certificate metadata collected as evidence

For the Week 2 system baseline increment, the read-only collector should gather host-level facts and package them as timestamped evidence. It should not install packages, restart services, rewrite configuration, or silently remediate the target.

### Evidence package

The evidence package should include:

- evidence identifier
- observed object
- host identifier
- source system
- collector metadata
- collection method
- timestamp in UTC
- evidence type
- raw or normalized technical facts
- integrity metadata
- policy evaluation reference

See [`examples/sample_evidence.json`](examples/sample_evidence.json).

For the Week 2 system baseline example, see [`examples/sample_system_baseline.json`](examples/sample_system_baseline.json).

For the Week 3 minimum evidence object, see [`examples/minimal_evidence_object.json`](examples/minimal_evidence_object.json).

### Integrity verification

A SHA256 hash is used as a minimal tamper-evident check for the evidence package.

A hash does not prove compliance. It proves whether the evidence changed after collection.

If evidence integrity verification fails, policy evaluation should not run. The correct result is not `pass` or `fail`; it is `invalid_evidence`.

See [`examples/invalid_evidence_result.json`](examples/invalid_evidence_result.json).

### Fact derivation

Python can be used to derive facts from raw evidence. For the TLS demo, derived facts may include:

- days until certificate expiry
- whether the certificate expires within a defined threshold
- signature algorithm family
- public key strength

### Policy evaluation

OPA/Rego evaluates verified facts against policy logic.

OPA should not evaluate raw, untrusted evidence. It should evaluate verified and normalized facts.

OPA is not the audit system. It is a policy evaluator.

### Audit narrative

The final report should translate the policy result into an audit narrative. It should avoid overclaiming regulatory meaning.

See [`examples/sample_report.md`](examples/sample_report.md).

## What This Demo Shows

This demo shows that a technical compliance finding can be built from a verifiable chain:

- read-only collection
- timestamped evidence
- integrity checking
- derived facts
- policy evaluation
- audit narrative generation

It demonstrates a pattern:

**Where technical evidence exists, compliance conclusions should be replayable.**

## What This Demo Does Not Show

This demo does not prove complete MAS TRM compliance.

It does not replace auditors, risk owners, regulatory interpretation, or legal advice.

It does not cover governance, outsourcing, incident response, change management, access control, resilience, or third-party risk.

It does not claim that SHA256 alone is sufficient for enterprise-grade evidence assurance. Production systems may require signed manifests, trusted timestamping, immutable storage, key management, approval workflows, and independent validation.

## Repository Structure

Planned structure:

```text
/ansible
/collector
/crypto
/opa
/reports
/examples
/docs
```

Current structure:

```text
evidence-validation-pipeline/
├── README.md
├── NOTICE.md
├── ansible/
│   └── collect_system_info.yml
├── docs/
│   └── week-3-evidence-before-reporting.md
└── examples/
    ├── invalid_evidence_result.json
    ├── minimal_evidence_object.json
    ├── sample_evidence.json
    ├── sample_report.md
    └── sample_system_baseline.json
```

## Related Concepts

- MAS TRM-inspired compliance automation
- read-only evidence collection
- non-invasive collection
- failure observability
- evidence events
- replayable evidence
- verifiable compliance
- evidence-as-code
- policy-as-code
- cryptographic evidence
- audit automation
- TLS certificate lifecycle
- evidence provenance
- timestamped evidence
- integrity verification
- invalid evidence

## Notes

**MAS TRM** refers to the **Monetary Authority of Singapore Technology Risk Management Guidelines**.
Official MAS page: https://www.mas.gov.sg/regulation/guidelines/technology-risk-management-guidelines

**OPA** refers to Open Policy Agent. **Rego** is its policy language.
Official OPA documentation: https://www.openpolicyagent.org/docs
