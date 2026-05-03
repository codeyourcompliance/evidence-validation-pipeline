# Evidence Validation Pipeline
![From Documentation to Evidence-Based Compliance](assets/images/From%20Documentation%20to%20Evidence-Based%20Compliance.png)
> A minimal MAS TRM-inspired evidence pipeline for replayable compliance automation.

This repository demonstrates the first CodeYourCompliance technical pattern:

**Compliance is not documentation. It is evidence that can be replayed.**

The goal is to show how a technical compliance finding can be derived from timestamped, integrity-checked, machine-evaluable evidence rather than from static screenshots, manual checklists, or after-the-fact reports.

This project is an architecture and demo asset. It is not legal, regulatory, audit, or certification advice.

## Purpose

The `evidence-validation-pipeline` project shows how to move from a static audit narrative to a replayable evidence workflow.

The minimal pipeline is:

1. Collect evidence from a target system in read-only mode.
2. Bind the evidence to a timestamp.
3. Generate an integrity hash for the evidence package.
4. Verify the evidence before policy evaluation.
5. Derive machine-readable facts.
6. Evaluate the facts with policy-as-code.
7. Generate a MAS TRM-aligned audit narrative.

The first demo scenario uses Apache HTTPD with TLS enabled. The target system is intentionally configured with a TLS certificate approaching expiry, such as within 48 hours, so the pipeline can produce a clear technical finding.

## Related Article

This repository accompanies the Week 1 CodeYourCompliance article:

**Compliance Is Not Documentation. It Is Evidence That Can Be Replayed.**

Substack: https://codeyourcompliance.substack.com/p/compliance-is-not-documentation-it-18e

The article introduces the core thesis behind this repository: compliance evidence should be collectible, timestamped, integrity-checked, machine-evaluable, and replayable.

## Content Relationship

- **Substack article:** explains the problem language and architecture thesis.
- **This repository:** stores the sample evidence structure, report example, and future implementation assets.
- **Future releases:** will add read-only collection, schema validation, integrity verification, and OPA/Rego policy examples.

## Architecture Overview
![Evidence Validation Pipeline](assets/images/Evidence%20Validation%20Pipeline.png)

In prose, the flow is simple:

System state is collected in read-only mode, packaged as timestamped evidence, checked for integrity, converted into derived facts, evaluated through policy logic, and finally translated into an audit narrative.

## Components

### Read-only collection

Ansible is used as the collection mechanism. The collector should observe the target system without modifying it.

The first demo assumes:

- Rocky Linux 10 as the audit controller
- Rocky Linux 9 as the Apache HTTPD target
- Apache HTTPD with TLS enabled
- TLS certificate metadata collected as evidence

### Evidence package

The evidence package should include:

- evidence identifier
- host identifier
- collector metadata
- timestamp in UTC
- evidence type
- raw or normalized technical facts
- integrity metadata

See [`examples/sample_evidence.json`](examples/sample_evidence.json).

### Integrity verification

A SHA256 hash is used as a minimal tamper-evident check for the evidence package.

If evidence integrity verification fails, policy evaluation should not run. The correct result is not `pass` or `fail`; it is `invalid_evidence`.

### Fact derivation

Python can be used to derive facts from raw evidence. For the TLS demo, derived facts may include:

- days until certificate expiry
- whether the certificate expires within a defined threshold
- signature algorithm family
- public key strength

### Policy evaluation

OPA/Rego evaluates verified facts against policy logic.

OPA should not evaluate raw, untrusted evidence. It should evaluate verified and normalized facts.

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

Current Week 1 structure:

```text
evidence-validation-pipeline/
├── README.md
└── examples/
    ├── sample_evidence.json
    └── sample_report.md
```

## Related Concepts

- MAS TRM-inspired compliance automation
- replayable evidence
- verifiable compliance
- evidence-as-code
- policy-as-code
- cryptographic evidence
- audit automation
- TLS certificate lifecycle

## Notes

**MAS TRM** refers to the **Monetary Authority of Singapore Technology Risk Management Guidelines**.
Official MAS page: https://www.mas.gov.sg/regulation/guidelines/technology-risk-management-guidelines

**OPA** refers to Open Policy Agent. **Rego** is its policy language.
Official OPA documentation: https://www.openpolicyagent.org/docs
