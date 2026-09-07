# Control-to-Evidence Mapping Example

This synthetic example isolates one evidence-engineering problem:

```text
valid evidence
!=
sufficient evidence
```

The control requires two independent evidence types before downstream policy evaluation is allowed.

## Files

- `control-evidence-map.json`
- `evidence-set-complete.json`
- `evidence-set-incomplete.json`

## Synthetic Control

The declared control claim requires both:

```text
tls_certificate_state
tls_runtime_protocol_state
```

The mapping rule is:

```text
all required evidence requirements must be satisfied
before downstream policy evaluation is allowed
```

This is an evidence-sufficiency rule.

It is not the downstream control policy.

## Complete Evidence Set

The complete example contains one admissible evidence reference for each required evidence type.

Its state is:

```text
evidence_set_status = complete
policy_evaluation_allowed = true
control_status = not_evaluated
```

The example deliberately stops before control evaluation.

A complete evidence set does not itself prove control pass or fail.

## Incomplete Evidence Set

The incomplete example contains admissible certificate-state evidence but no runtime protocol-state evidence.

Its state is:

```text
evidence_set_status = incomplete
policy_evaluation_allowed = false
control_status = unknown
```

The certificate evidence did not become invalid.

The missing protocol evidence did not become a failed control.

The required proof set is incomplete.

## Comparison

| Field | Complete set | Incomplete set |
| --- | --- | --- |
| Required requirements | 2 | 2 |
| Satisfied requirements | 2 | 1 |
| Present evidence admissible | yes | yes |
| Missing required evidence | none | `REQ-TLS-PROTOCOL-STATE` |
| Evidence-set status | `complete` | `incomplete` |
| Policy evaluation allowed | `true` | `false` |
| Control result | not evaluated | `unknown` |

## What the Example Shows

Object-level admissibility and set-level sufficiency are separate gates.

The useful boundary is:

```text
all present evidence admissible
+ required evidence missing
-> evidence set incomplete
-> control evaluation blocked
-> control status unknown
```

Missing evidence is not proof of control failure.

## What the Example Does Not Show

It does not prove that the declared two-requirement mapping is the correct control design.

It does not execute OPA.

It does not assemble evidence automatically.

It does not implement control-catalog governance.

It does not cryptographically bind the mapping artifact to an assessment result.

Those are separate implementation problems.

## Origin and Scope

This artifact originates from **CodeYourCompliance**.

- Website: https://www.codeyourcompliance.com/
- GitHub organization: https://github.com/codeyourcompliance
- Original repository: https://github.com/codeyourcompliance/evidence-validation-pipeline

Attribution is requested for forks, references, adaptations, and discussions.

MAS TRM-inspired means engineering interpretation. This example does not provide legal, regulatory, audit, certification, compliance, procurement, or implementation advice.
