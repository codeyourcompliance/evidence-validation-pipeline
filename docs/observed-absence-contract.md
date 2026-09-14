# Observed Absence Evidence Contract

An empty result is not automatically negative evidence.

A source may have been queried successfully and shown that an expected object is absent.

Or the collector may have failed before it could observe the source at all.

Those states must remain different.

This document defines a narrow CodeYourCompliance boundary:

```text
observed absence
!=
failed observation
```

## Scope

This document is part of the CodeYourCompliance `evidence-validation-pipeline` repository.

It is a MAS TRM-inspired engineering artifact. It is not legal, regulatory, audit, certification, compliance, procurement, or implementation advice.

The examples are synthetic and illustrative.

The goal is not to prove that absence satisfies a control.

The goal is to preserve enough collection outcome semantics to distinguish an observed absence from a failed or incomplete observation.

## Failure Mode

A collector expects to retrieve a configuration object.

The resulting payload contains no object.

A downstream normalizer converts the result to:

```text
configured = false
```

That conversion may be valid if the source was reached, the query completed, the intended scope was covered, and the source semantics make absence meaningful.

It is not valid if the same empty state came from a timeout, authorization failure, incomplete pagination, filtered scope, or collector error.

Without collection-outcome semantics, both cases can collapse into the same Boolean value.

## Minimum Observation Outcome

A minimal observation outcome record should preserve:

```yaml
observation_outcome:
  source_ref:
  collection_method:
  collection_attempted:
  collection_status:
  query_semantics_ref:
  scope_ref:
  scope_reached:
  response_status:
  result_completeness:
  observed_state:
  absence_assertion_supported:
  failure_reason:
  observed_at_utc:
```

### `source_ref`

Identifies the source that was expected to answer the observation.

Observed absence is meaningful only relative to a defined source.

### `collection_method`

Records how the source was queried.

Examples include read-only API query, CLI command, file inspection, database query, or runtime probe.

The method affects what an empty result means.

### `collection_attempted`

Records whether the collection attempt actually started.

A scheduled task that never ran cannot produce negative evidence about the target state.

### `collection_status`

Distinguishes successful collection from failed, partial, or indeterminate collection.

A failed collection does not establish source absence.

### `query_semantics_ref`

Identifies the query or collection semantics used to interpret presence and absence.

For some APIs, an empty array means no matching objects.

For others, an empty result may mean insufficient permission, filtering, pagination, or an unsupported endpoint.

The interpretation must not be assumed from payload shape alone.

### `scope_ref` and `scope_reached`

Identify the intended observation scope and whether that scope was actually reached.

Evidence from the wrong host, account, region, namespace, endpoint, or object scope cannot support an absence claim for the intended target.

### `response_status`

Records the source or transport response relevant to interpretation.

Examples include HTTP 200, command exit code 0, timeout, authentication failure, or connection refused.

Transport success alone does not establish observation completeness.

### `result_completeness`

Records whether the collector completed the operation needed to interpret the result.

Examples include:

```text
complete
partial
unknown
not_observed
```

A first page containing no matches is not evidence of absence if additional pages were never checked.

### `observed_state`

Preserves the semantic outcome without collapsing different failure states.

A narrow state set may include:

```text
present
observed_absent
unobserved
indeterminate
```

`observed_absent` means the source was successfully observed and the defined query semantics support an absence assertion.

`unobserved` means the intended source state was not obtained.

### `absence_assertion_supported`

Records whether the collection outcome supports an explicit absence assertion.

This field does not mean the control passes.

It means the observation path supports the narrower statement that the queried object or condition was absent in the declared scope at the observation time.

### `failure_reason`

Preserves why the source was not observed when collection did not complete.

Examples include timeout, authentication failure, permission denied, parser error, rate limit, or unreachable target.

### `observed_at_utc`

Records when the source state was actually observed.

If no observation occurred, the collection attempt time must not be presented as successful observation time.

## Observed Absence Has Preconditions

An empty payload is not enough.

Before an absence assertion is usable, the collection path should establish at least:

```text
intended source reached
+ intended scope reached
+ query completed
+ result completeness established
+ absence semantics defined
```

Only then can an empty or missing object be modeled as `observed_absent`.

The boundary is:

```text
successful complete observation
+ defined absence semantics
+ no matching object
-> observed_absent
```

This still does not establish control pass.

It produces an evidence state that a downstream control may or may not use.

## Collection Failure Is Not Negative Evidence

The prohibited shortcut is:

```text
no returned object
=> object absent
```

when collection did not complete.

A timeout should remain closer to:

```text
collection_status = failed
observed_state = unobserved
absence_assertion_supported = false
control_status = unknown
```

The collector learned that observation failed.

It did not learn that the target object was absent.

## Empty Response Is Not Always Observed Absence

Even a technically successful request can be insufficient.

Examples include:

- only the first page was queried
- the authenticated identity could not see all objects
- a filter excluded the target object
- the request reached the wrong scope
- the endpoint returns an empty result for unsupported fields
- the collector parser discarded an unrecognized result

For that reason:

```text
transport success
!=
observation completeness
```

An absence assertion requires collection semantics, not just a green HTTP status.

## Negative Evidence Is Still Evidence With Scope

An observed absence is bounded by source, method, scope, and time.

For example:

```text
No matching legacy TLS protocol configuration was observed
for synthetic-endpoint-443
through query X
at timestamp T.
```

That is narrower than:

```text
Legacy TLS is disabled everywhere.
```

The first statement describes an observation.

The second is a broader control or environment conclusion and requires additional evidence and policy logic.

## Relationship to Evidence Sufficiency

The control-to-evidence mapping contract asks whether the declared proof set is complete.

This contract answers an earlier question: what state should a collection outcome have before it is admitted into that proof set?

A required evidence item can therefore be:

```text
present
observed_absent
unobserved
indeterminate
```

Whether `observed_absent` satisfies a particular evidence requirement depends on the control-to-evidence mapping and downstream policy semantics.

`unobserved` should not silently satisfy a requirement that expects negative evidence.

## Synthetic Example

See [`examples/observed-absence/`](../examples/observed-absence/).

The examples compare two synthetic collection outcomes for the same declared target and query semantics.

The first models a completed query with no matching object and records `observed_state = observed_absent`.

The second models a timeout before source state was obtained and records `observed_state = unobserved`.

Neither example executes a real collector, admissibility gate, sufficiency gate, OPA policy, or control evaluation.

The recorded states are synthetic scenario assertions.

## Current Implementation Boundary

This repository currently models observed absence versus failed observation through this contract and synthetic examples.

It does not yet implement generic query-semantic validation.

It does not automatically verify pagination, authorization completeness, or source authority across evidence types.

It does not automatically determine whether an observed absence satisfies a control requirement.

It does not cryptographically bind query semantics or observation outcome records to evidence packages.

Those are separate implementation steps.

## Origin and Attribution

This artifact originates from **CodeYourCompliance**.

- Website: https://www.codeyourcompliance.com/
- GitHub organization: https://github.com/codeyourcompliance
- Original repository: https://github.com/codeyourcompliance/evidence-validation-pipeline

Attribution is requested for forks, references, adaptations, and discussions.

## Final Boundary

No returned object can mean absence.

It can also mean the observation failed.

The evidence record must preserve which one happened.