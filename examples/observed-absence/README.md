# Observed Absence vs Failed Observation

This synthetic example isolates one collection-outcome boundary:

```text
observed absence
!=
failed observation
```

Both scenarios target the same synthetic endpoint and use the same declared query semantics.

## Files

- `observed-absence.json`
- `collection-failure.json`

## Scenario A — Observed Absence

The collector is modeled as reaching the intended source and scope successfully.

The query completes with no matching legacy TLS protocol configuration.

The modeled outcome is:

```text
collection_status = success
result_completeness = complete
observed_state = observed_absent
absence_assertion_supported = true
control_status = not_evaluated
```

This is negative evidence only at the observation layer.

It does not itself prove that a control passes.

## Scenario B — Collection Failure

The same intended query times out before the source state is obtained.

The modeled outcome is:

```text
collection_status = failed
result_completeness = not_observed
observed_state = unobserved
absence_assertion_supported = false
control_status = unknown
```

No object was returned in either scenario.

Only the first scenario supports an absence assertion.

## Execution Boundary

These files are synthetic scenario models.

They are explicitly marked as non-runtime captures.

No real collector, evidence-admissibility gate, evidence-sufficiency gate, OPA policy, or control evaluation is executed to produce these states.

## What the Example Shows

The useful boundary is:

```text
no matching object
+ complete observation
+ defined absence semantics
-> observed_absent
```

versus:

```text
no returned object
+ failed observation
-> unobserved
```

A pipeline should not normalize both outcomes to the same Boolean value.

## What the Example Does Not Show

It does not prove that the synthetic source is authoritative for a real control.

It does not validate pagination, permissions, or query semantics automatically.

It does not prove that `observed_absent` satisfies a control requirement.

It does not implement negative-evidence policy logic.

Those remain separate problems.

## Origin and Scope

This artifact originates from **CodeYourCompliance**.

- Website: https://www.codeyourcompliance.com/
- GitHub organization: https://github.com/codeyourcompliance
- Original repository: https://github.com/codeyourcompliance/evidence-validation-pipeline

Attribution is requested for forks, references, adaptations, and discussions.

MAS TRM-inspired means engineering interpretation. This example does not provide legal, regulatory, audit, certification, compliance, procurement, or implementation advice.