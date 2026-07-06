# Workflow Proof Boundary

Tool approval is not workflow proof.

Approval controls entry.

Workflow proof controls consequence.

## Scope

This document defines the Week 9 boundary for the CodeYourCompliance `evidence-validation-pipeline` repository.

It is a MAS TRM-inspired engineering artifact. It is not legal, regulatory, audit, or certification advice.

This document does not implement a workflow-proof engine.

It defines the evidence boundary that such an engine would need to preserve.

## Problem

An AI tool may be approved for internal use.

That approval may show:

- the tool was reviewed
- access was allowed
- a policy owner approved use
- a user or group may use the tool
- a vendor or system passed an intake process

That is entry control.

It does not prove that a specific AI-supported workflow action was controlled.

## Boundary

A workflow-proof record should preserve the action path, not only the tool approval record.

Minimum fields include:

| Field | Purpose |
| --- | --- |
| `workflow_action_id` | Identifies the specific action under review. |
| `tool_id` | Identifies the approved tool used in the workflow. |
| `approval_record_id` | Links to the tool approval or access approval record. |
| `task_scope` | States what task the AI-supported workflow performed. |
| `data_scope` | States what data was used or accessed. |
| `policy_version` | Identifies the policy or rule version in force at the time. |
| `review_required` | States whether human review was required before consequence. |
| `review_owner` | Identifies who or what owned the review step. |
| `accepted_output` | Records whether the output was accepted, rejected, or modified. |
| `failure_path` | Describes what should happen if the workflow fails or evidence is incomplete. |
| `collector_metadata` | Identifies how the workflow evidence was collected. |
| `collected_at_utc` | Binds the evidence to collection time. |
| `integrity_status` | States whether the evidence object passed integrity verification. |

## Evidence Chain

The minimum chain is:

```text
tool approval record
-> workflow action record
-> data and task scope
-> review requirement
-> accepted output
-> failure path
-> evidence verification
-> policy evaluation
-> audit narrative
```

A tool approval record may be part of the evidence package.

It should not be the whole package.

## Invalid Evidence Conditions

Workflow proof should not be produced if:

- the workflow action is not identified
- the task scope is missing
- the data scope is missing
- review requirement is unknown
- accepted output is not recorded
- policy version is missing
- failure path is undefined
- evidence integrity fails
- the audit narrative cannot reference the evaluated evidence object

The correct state is `invalid_evidence`, not `pass` or `fail`.

## Related Examples

- [`examples/minimal_workflow_proof_object.json`](../examples/minimal_workflow_proof_object.json)
- [`examples/invalid_workflow_proof_missing_review_owner.json`](../examples/invalid_workflow_proof_missing_review_owner.json)

The first example shows a minimum workflow-proof evidence object.

The second example shows why missing review ownership should produce `invalid_evidence`, not a clean pass or fail result.

## Boundary Statement

A tool may be approved.

A workflow may still be unproven.

Access governance is not consequence control.
