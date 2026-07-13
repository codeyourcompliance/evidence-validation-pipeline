# Evidence Contract Boundary

An integration can move data.

It does not automatically preserve audit meaning.

This document defines a narrow CodeYourCompliance boundary:

```text
Integration = transport.
Evidence contract = audit meaning.
```

## Scope

This document is part of the CodeYourCompliance `evidence-validation-pipeline` repository.

It is a MAS TRM-inspired engineering artifact. It is not legal, regulatory, audit, certification, compliance, procurement, or implementation advice.

The examples are synthetic and illustrative.

The goal is not to prove MAS TRM compliance.

The goal is to make the transport-versus-evidence boundary visible before synchronized data becomes accepted audit evidence.

## Failure Mode

A compliance platform connects to a source system.

Authentication succeeds.

A payload arrives.

The destination marks the integration as successful.

A reviewer later asks:

- Which source produced the value?
- Which collector and collector version retrieved it?
- When was the source state observed?
- Was the expected scope fully reached?
- Were any targets unreachable?
- Was the payload transformed?
- Was the record modified after collection?
- Which policy evaluation consumed it?

If the transported record cannot answer those questions, transport succeeded but the evidence contract failed.

## Boundary

A working integration may prove:

- credentials were accepted
- an endpoint was reachable
- a payload was returned
- field mapping executed
- data reached the destination

It does not automatically prove:

- the source was authoritative
- the collection scope was complete
- failed collection remained visible
- the evidence was fresh
- the evidence was integrity-checked
- normalization preserved meaning
- the record was admissible as policy input
- the policy result can be replayed

A successful synchronization is not an audit conclusion.

## Minimum Evidence Contract

A minimal evidence contract should preserve:

```yaml
evidence_contract:
  source_system:
  collector:
  collector_version:
  collection_method:
  timestamp_utc:
  evidence_type:
  evidence_layer:
  integrity_hash:
  validation_status:
  policy_input_ref:
```

### `source_system`

Identifies the system or authoritative source that produced the observed state.

A copied value without a source reference is difficult to challenge or replay.

### `collector`

Identifies the process that observed the source.

The collector may be an Ansible playbook, API client, script, agent, export job, or manual process.

### `collector_version`

Identifies the implementation version that produced the record.

Collector behavior may change across versions.

### `collection_method`

Records how the state was collected.

Examples include read-only API query, file export, database query, runtime probe, screenshot, or manual observation.

Collection method is part of the audit boundary.

### `timestamp_utc`

Records when the source state was observed.

Display time is not observation time.

### `evidence_type`

Defines what kind of evidence object was collected.

Examples include system baseline, certificate state, access configuration, service state, approval record, or exception record.

### `evidence_layer`

Separates raw evidence from later transformations.

```text
raw_evidence
-> normalized_fact
-> derived_fact
-> policy_input
-> policy_result
-> audit_narrative
```

A derived fact is not the original observation.

A report is not raw evidence.

### `integrity_hash`

Supports detection of post-collection mutation.

A hash does not prove that the original observation was correct.

It proves whether the preserved object changed after sealing.

### `validation_status`

Preserves whether the evidence is valid, invalid, missing, stale, tampered, unknown, or not machine-verifiable.

Weak evidence states must not be silently converted into pass or fail.

### `policy_input_ref`

Links the evidence object to the policy evaluation that consumed it.

A policy result without an input reference is difficult to replay.

## Scope Must Survive Transport

Suppose a collector is expected to inspect 100 targets.

It reaches 94.

The integration writes 94 records into the destination.

The correct evidence state is:

```text
expected_targets: 100
observed_targets: 94
failed_collection: 6
```

It is not:

```text
environment_status: compliant
```

The six missing targets did not pass.

They did not fail the control either.

They were not observed.

```text
missing evidence != control failure
missing evidence != control pass
missing evidence = unresolved evidence state
```

If the integration drops that distinction, the destination contains incomplete evidence with a clean transport result.

## Status Separation

Do not use one status field for the whole pipeline.

```json
{
  "status": "success"
}
```

That field does not show what succeeded.

Use separate statuses:

```yaml
transport_status: success
collection_status: partial
schema_status: valid
integrity_status: verified
freshness_status: stale
policy_status: not_evaluated
control_status: unknown
```

A single green status is easy to display.

It is difficult to audit.

## Normalization Is Not Neutral

Integrations rename fields, convert timestamps, flatten objects, infer Boolean values, and discard unsupported data.

Those transformations may be necessary.

They change evidentiary meaning.

If a source field is converted into a derived conclusion, preserve:

- source field
- source value
- transformation rule
- transformation version
- evaluation timestamp
- derived fact

Otherwise the integration replaces evidence with an unexplained conclusion.

## Failure Outcomes

The pipeline should distinguish:

```text
transport_failure
collection_failure
invalid_evidence
policy_evaluation_failure
control_failure
```

An API timeout is not automatically non-compliance.

The defensible sequence is:

```text
API timeout
-> collection incomplete
-> evidence missing
-> control not evaluated
-> review or escalation required
```

Control failure should be recorded only when valid evidence was evaluated and the required condition was not met.

## Synthetic Examples

- [`integration_without_evidence_contract.json`](../examples/integration_without_evidence_contract.json)
- [`integration_with_evidence_contract.json`](../examples/integration_with_evidence_contract.json)

The first example shows successful transport with missing provenance, scope, integrity, and policy linkage.

The second shows the same synthetic integration with those evidence semantics preserved.

These examples do not implement a complete integration governance or evidence integrity model.

They show one boundary:

```text
successful transport does not establish evidence validity
```

## Origin and Attribution

This artifact originates from **CodeYourCompliance**.

- Website: https://www.codeyourcompliance.com/
- GitHub organization: https://github.com/codeyourcompliance
- Original repository: https://github.com/codeyourcompliance/evidence-validation-pipeline

Attribution is requested for forks, references, adaptations, and discussions.

## Final Boundary

An integration moves data.

An evidence contract preserves what the data means.

Transport is necessary.

Meaning must survive it.
