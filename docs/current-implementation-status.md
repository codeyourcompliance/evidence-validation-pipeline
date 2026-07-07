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
| Stale evidence example | `examples/stale_evidence.json` |
| Evidence freshness policy demo | `policies/demo/evidence_freshness.rego` |
| Minimum workflow-proof evidence object | `examples/minimal_workflow_proof_object.json` |
| Invalid workflow-proof evidence result | `examples/invalid_workflow_proof_missing_review_owner.json` |
| Sample audit narrative | `examples/sample_report.md` |
| Evidence replay checklist | `docs/evidence-replay-checklist.md` |
| Screenshot evidence classification | `docs/screenshot-evidence-gap.md` |
| Evidence-before-reporting boundary | `docs/week-3-evidence-before-reporting.md` |
| Workflow-proof boundary | `docs/workflow-proof-boundary.md` |

## Modeled

The repository models these boundaries:

- observation vs remediation
- checklist row vs evidence requirement
- screenshot vs proof object
- evidence processing vs audit conclusion
- delivery evidence vs workflow evidence
- tool approval vs workflow proof
- evidence integrity vs evidence freshness
- stale evidence vs failed control
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
- full OPA/Rego policy pack
- replay runner
- workflow-level policy evaluation
- end-to-end evidence package generation

The workflow-proof examples are synthetic evidence objects.

They are not a full workflow-proof engine.

The freshness policy is a narrow demo policy.

It is not a complete evidence integrity policy pack.

## Design Rule

Do not evaluate a control claim from weak evidence.

If evidence integrity fails, policy evaluation should not run.

If evidence freshness has expired, downstream policy evaluation should be blocked or explicitly marked as stale evidence.

If the evidence source is unclear, classify the artifact before using it.

If the artifact is only a claim, treat it as a claim.

## Boundary Statement

This repository is an evidence engineering demonstration.

It does not claim MAS TRM compliance.

It does not replace formal control ownership, risk assessment, audit review, or regulatory interpretation.

The audit boundary starts before the report.
