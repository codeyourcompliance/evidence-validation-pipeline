# Transformation Provenance Contract

A normalized fact is not the original observation.

Transformation logic is part of the evidence chain.

This document defines a narrow CodeYourCompliance boundary:

```text
raw observation
!=
normalized fact
```

## Scope

This document is part of the CodeYourCompliance `evidence-validation-pipeline` repository.

It is a MAS TRM-inspired engineering artifact. It is not legal, regulatory, audit, certification, compliance, procurement, or implementation advice.

The examples are synthetic and illustrative.

The goal is not to prove that a transformation rule is correct.

The goal is to preserve enough transformation provenance to distinguish a target-state change from a change in normalization logic.

## Failure Mode

A source system returns the same raw value in two assessments.

The later evidence package contains a different normalized fact.

The report calls this system drift.

But the normalization rule also changed.

The first rule maps a source value to `false`.

The second preserves the same source value as `unknown`.

The target observation did not change in the synthetic scenario.

The interpretation did.

If transformation provenance is missing, the evidence package cannot separate those possibilities.

## Minimum Transformation Provenance

A minimal transformation provenance record should preserve:

```yaml
transformation:
  name:
  version:
  type:
  rule_id:
  rule_version:
  input_ref:
  input_field:
  input_value:
  output_field:
  output_value:
  output_state:
  executed_at_utc:
```

### `name`

Identifies the component that transformed the source observation.

### `version`

Identifies the transformation implementation version.

A normalized fact produced by version `0.1.0` should not be assumed equivalent to one produced by version `0.2.0` when the mapping logic changed.

### `type`

Identifies the transformation stage, such as `normalization`, `parsing`, or `derivation`.

This contract focuses on normalization.

### `rule_id` and `rule_version`

Identify the rule that mapped the input to the output.

The rule identity should survive with the normalized fact.

### `input_ref`

Links the transformation to the raw evidence object or source observation it consumed.

A normalized value without an input reference is difficult to challenge or replay.

### `input_field` and `input_value`

Preserve the source field and source value used by the transformation.

### `output_field`, `output_value`, and `output_state`

Preserve the normalized result.

`output_state` is useful when the normalized value cannot be represented safely as a simple Boolean or scalar.

For example, `unknown` should not be silently converted into `false`.

### `executed_at_utc`

Records when the transformation ran.

Transformation provenance should travel with the normalized fact that later becomes policy input.

## Transformation Change Is Not Target Drift

The prohibited shortcut is:

```text
different normalized fact
-> target drift
```

when the transformation rule also changed.

The safer interpretation is:

```text
same raw observation
+ transformation changed
-> normalized fact changed
-> transformation difference must be resolved
-> target drift not established by this difference alone
```

A transformation change does not prove that the target did not change in a real environment.

It means the evidence pipeline must not attribute a changed normalized result to the target without preserving the transformation path.

## Raw Observation and Normalized Fact Are Different Evidence Layers

The existing evidence contract separates:

```text
raw_evidence
-> normalized_fact
-> derived_fact
-> policy_input
-> policy_result
-> audit_narrative
```

That separation is intentional.

The raw observation records what the source returned.

The normalized fact records how that observation was represented for later processing.

The two objects may contain related data.

They do not have the same evidentiary meaning.

## Integrity Does Not Validate Interpretation

A hash can show whether a preserved evidence object changed after sealing.

It does not prove that a transformation rule interpreted the source correctly before sealing.

For example:

```text
source value: not_configured
normalization: not_configured -> false
integrity: verified
```

The verified hash protects the preserved object from undetected mutation.

It does not establish that `false` was the correct normalization.

Integrity and transformation correctness are separate problems.

## Transformation Provenance Is Not Transformation Correctness

Recording transformation metadata does not make the transformation authoritative.

A named rule can still be wrong.

A versioned normalizer can still contain a bug.

A documented mapping can still be inappropriate for the control being evaluated.

Transformation provenance answers:

```text
How was this normalized fact produced?
```

It does not automatically answer:

```text
Was this transformation correct?
```

That remains a separate validation problem.

## Synthetic Example

See [`examples/transformation-provenance/`](../examples/transformation-provenance/).

The example holds a synthetic target-state identifier and raw observation constant by construction.

The raw source value is:

```text
status = not_configured
```

Normalization version `0.1.0` maps that value to:

```text
enabled = false
```

Normalization version `0.2.0` preserves the unresolved state as:

```text
enabled = null
state = unknown
```

The example does not establish which normalization rule is correct.

It shows one boundary:

```text
same raw observation
+ different transformation logic
-> different normalized fact
!= target-state change
```

## Current Implementation Boundary

This repository currently models transformation provenance through structured metadata and synthetic examples.

It does not yet cryptographically bind transformation source code, parser artifacts, normalizer artifacts, or rule digests to each normalized fact.

It does not yet provide automated transformation-version equivalence or regression testing.

It does not yet enforce one repo-wide transformation provenance schema across every evidence type.

Those are separate implementation steps.

## Origin and Attribution

This artifact originates from **CodeYourCompliance**.

- Website: https://www.codeyourcompliance.com/
- GitHub organization: https://github.com/codeyourcompliance
- Original repository: https://github.com/codeyourcompliance/evidence-validation-pipeline

Attribution is requested for forks, references, adaptations, and discussions.

## Final Boundary

Normalization is not neutral transport.

It creates a new evidence layer.

If the rule, version, input, or output path disappears, part of the evidence history disappears with it.
