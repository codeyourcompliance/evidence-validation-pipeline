# Policy Evaluation Provenance Example

This synthetic example isolates one evidence-engineering problem:

```text
A changed control result does not automatically prove target drift when the policy semantics also changed.
```

The scenario holds one synthetic policy input constant by construction.

Only the policy artifact changes.

## Files

- `policy-input.json`
- `policy-v0.1.0.rego`
- `policy-v0.2.0.rego`
- `expected-evaluation-v0.1.0.json`
- `expected-evaluation-v0.2.0.json`

## Fixed Policy Input

Both policy versions consume:

```text
days_to_expiry = 30
minimum_certificate_days_remaining = 30
```

The synthetic target-state identifier, normalized fact, and evaluation context remain constant by scenario construction.

The policy-input SHA256 is:

```text
5eecf4476ef75731b7302d7740014e7a4620e1726c85dd7d5252238fec033647
```

## Policy Comparison

Version `0.1.0` uses:

```text
days_to_expiry >= minimum_certificate_days_remaining
```

Its modeled expected result is:

```text
PASS
```

Version `0.2.0` uses:

```text
days_to_expiry > minimum_certificate_days_remaining
```

Its modeled expected result is:

```text
FAIL
```

| Field | v0.1.0 | v0.2.0 |
| --- | --- | --- |
| Policy input | same | same |
| Target-state ID | `tls-target-state-002` | `tls-target-state-002` |
| Days to expiry | `30` | `30` |
| Minimum days | `30` | `30` |
| Policy rule | `>=` | `>` |
| Policy SHA256 | `8e57f9f9...` | `ed4e89b7...` |
| Modeled result | `pass` | `fail` |

## What the Example Shows

The result difference is caused by a policy semantic difference inside the synthetic scenario.

The point is narrow:

```text
same policy input
+ different policy semantics
-> different decision
-> target-state change is not established by this difference alone
```

A policy change does not prove that a real target remained unchanged between two assessments.

The constant target-state identifier and policy input are synthetic scenario constraints used to isolate policy provenance.

## Expected Result Files Are Not Runtime Captures

The two `expected-evaluation-*.json` files are explicitly marked:

```text
execution.mode = synthetic_expected_result
policy_artifact_executed = false
decision_executed = false
runtime_capture = false
```

They model the expected semantic consequence of the two simple Rego expressions.

They do not claim that OPA was executed to produce those JSON files.

For an actual bounded replay implementation that records policy and input-related digests plus runtime provenance, see [`../replayable-tls-control/`](../replayable-tls-control/).

## Boundary

Policy provenance is not policy correctness.

A versioned and hashed policy can still encode the wrong threshold, operator, scope, exception behavior, or control interpretation.

Deterministic evaluation can reproduce a wrong policy faithfully.

The policy digest establishes which policy bytes were referenced.

It does not establish that those policy bytes were correct.

See [`docs/policy-evaluation-provenance-contract.md`](../../docs/policy-evaluation-provenance-contract.md).

## Origin and Scope

This artifact originates from **CodeYourCompliance**.

- Website: https://www.codeyourcompliance.com/
- GitHub organization: https://github.com/codeyourcompliance
- Original repository: https://github.com/codeyourcompliance/evidence-validation-pipeline

Attribution is requested for forks, references, adaptations, and discussions.

MAS TRM-inspired means engineering interpretation. This example does not provide legal, regulatory, audit, certification, or compliance advice.
