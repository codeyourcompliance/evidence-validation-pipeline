# Current Implementation Status

This document states what the `evidence-validation-pipeline` repository currently implements, what it models, and what remains out of scope.

The purpose is to avoid treating architecture language as finished implementation.

This repository is a MAS TRM-inspired engineering artifact. It is not legal, regulatory, audit, or certification advice.

## Implemented

The repository currently includes:

| Area | Current artifact |
| --- | --- |
| Read-only baseline collection | `ansible/collect_system_info.yml` |
| System baseline evidence example | `examples/sample_system_baseline.json` |
| TLS lifecycle evidence example | `examples/sample_evidence.json` |
| Minimum replay-aware evidence object | `examples/minimal_evidence_object.json` |
| Invalid evidence result | `examples/invalid_evidence_result.json` |
| Sample audit narrative | `examples/sample_report.md` |
| Evidence replay checklist | `docs/evidence-replay-checklist.md` |
| Screenshot evidence classification | `docs/screenshot-evidence-gap.md` |
| Evidence-before-reporting boundary | `docs/week-3-evidence-before-reporting.md` |

## Modeled

The repository models these boundaries:

- observation vs remediation
- checklist row vs evidence requirement
- screenshot vs proof object
- evidence processing vs audit conclusion
- delivery evidence vs workflow evidence
- tool approval vs workflow proof
- invalid evidence vs failed control

These boundaries are part of the public technical model.

They are not complete product features.

## Not Yet Implemented

The repository does not yet implement:

- full schema validation
- computed evidence hashes
- signed manifests
- trusted timestamping
- immutable evidence storage
- OPA/Rego policy files
- replay runner
- workflow-proof evidence objects
- workflow-level policy evaluation
- end-to-end evidence package generation

## Design Rule

Do not evaluate a control claim from weak evidence.

If evidence integrity fails, policy evaluation should not run.

If the evidence source is unclear, classify the artifact before using it.

If the artifact is only a claim, treat it as a claim.

## Boundary Statement

This repository is an evidence engineering demonstration.

It does not claim MAS TRM compliance.

It does not replace formal control ownership, risk assessment, audit review, or regulatory interpretation.

The audit boundary starts before the report.
