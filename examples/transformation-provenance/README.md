# Transformation Provenance Example

This synthetic example isolates one evidence-engineering problem:

```text
A changed normalized fact does not automatically prove target drift when the transformation logic also changed.
```

The scenario holds a synthetic target-state identifier and the raw observation constant by construction.

Only the normalization logic changes.

## Files

- `raw-observation.json`
- `normalized-v0.1.0.json`
- `normalized-v0.2.0.json`

The raw evidence object records:

```text
status = not_configured
```

Both normalization examples reference that same raw observation.

Version `0.1.0` maps the source value to:

```text
enabled = false
state = resolved
```

Version `0.2.0` preserves the unresolved source state as:

```text
enabled = null
state = unknown
```

## Comparison

| Field | v0.1.0 | v0.2.0 |
| --- | --- | --- |
| Target-state ID | `config-target-state-001` | `config-target-state-001` |
| Raw input field | `status` | `status` |
| Raw input value | `not_configured` | `not_configured` |
| Normalizer | `configuration-state-normalizer` | `configuration-state-normalizer` |
| Normalizer version | `0.1.0` | `0.2.0` |
| Rule ID | `MAP_NOT_CONFIGURED_TO_FALSE` | `PRESERVE_NOT_CONFIGURED_AS_UNKNOWN` |
| Output field | `enabled` | `enabled` |
| Output value | `false` | `null` |
| Output state | `resolved` | `unknown` |

The example does not establish which normalization rule is correct.

It does not prove that a real target could never change between two assessments.

The constant target-state identifier and raw observation are synthetic scenario constraints used to isolate transformation provenance.

The point is narrower:

```text
same raw observation
+ different transformation logic
-> different normalized fact
-> target-state change is not established by this difference alone
```

Before classifying a normalized difference as target-state drift, inspect the transformation path.

## Boundary

Transformation provenance is not transformation correctness.

Recording a rule ID and version makes the interpretation path inspectable.

It does not prove that the mapping is valid for a specific control.

The same distinction applies to integrity.

A verified hash can show that a normalized object was not modified after sealing.

It cannot prove that the normalization rule was semantically correct before sealing.

See [`docs/transformation-provenance-contract.md`](../../docs/transformation-provenance-contract.md).

## Origin and Scope

This artifact originates from **CodeYourCompliance**.

- Website: https://www.codeyourcompliance.com/
- GitHub organization: https://github.com/codeyourcompliance
- Original repository: https://github.com/codeyourcompliance/evidence-validation-pipeline

Attribution is requested for forks, references, adaptations, and discussions.

MAS TRM-inspired means engineering interpretation. This example does not provide legal, regulatory, audit, certification, or compliance advice.
