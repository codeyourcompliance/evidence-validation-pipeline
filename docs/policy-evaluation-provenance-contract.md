# Policy Evaluation Provenance Contract

A changed control result does not automatically mean the target changed.

The policy that produced the result may have changed instead.

This document defines a narrow CodeYourCompliance boundary:

```text
control result
!=
source-free decision
```

## Scope

This document is part of the CodeYourCompliance `evidence-validation-pipeline` repository.

It is a MAS TRM-inspired engineering artifact. It is not legal, regulatory, audit, certification, compliance, procurement, or implementation advice.

The examples are synthetic and illustrative.

The goal is not to prove that a policy is correct.

The goal is to preserve enough evaluation provenance to distinguish a decision change caused by policy semantics from a change in the target or evidence.

## Failure Mode

The same admissible policy input is evaluated twice.

The first assessment returns `pass`.

The second returns `fail`.

A later report calls this control drift.

But the policy artifact also changed.

If policy provenance is missing, the evidence package cannot show whether the changed result came from the target, the policy input, the evaluation context, the policy artifact, or the decision engine.

A result without its evaluation provenance is difficult to replay and difficult to challenge.

## Minimum Policy Evaluation Provenance

A minimal evaluation provenance record should preserve:

```yaml
evaluation:
  engine:
  engine_version:
  policy_id:
  policy_version:
  rule_id:
  rule_version:
  policy_artifact_ref:
  policy_artifact_sha256:
  policy_input_ref:
  policy_input_sha256:
  evaluation_context_ref:
  implementation_version:
  evaluated_at_utc:
  decision_executed:
  result:
```

### `engine` and `engine_version`

Identify the decision engine that executed the policy.

A policy artifact evaluated by different engine versions should not be assumed equivalent without testing.

### `policy_id` and `policy_version`

Identify the policy semantics used for the decision.

A current policy version cannot silently stand in for the version that produced a historical result.

### `rule_id` and `rule_version`

Identify the specific rule or decision entry point that produced the result.

A policy package may contain multiple rules with different meanings.

### `policy_artifact_ref` and `policy_artifact_sha256`

Identify the exact policy artifact and support detection of post-evaluation mutation.

A policy version label is useful metadata.

A digest binds the recorded evaluation to specific policy bytes more precisely.

A digest does not prove that the policy semantics are correct.

### `policy_input_ref` and `policy_input_sha256`

Identify the exact input consumed by the policy and support replay against the same bytes.

A result cannot be replayed from a policy artifact alone.

### `evaluation_context_ref`

Identifies external decision context when policy semantics depend on thresholds, dates, scope, jurisdiction, exception state, or other explicit context.

Policy input and evaluation context should not silently change between replays.

### `implementation_version`

Identifies the replay or evaluation implementation surrounding the policy engine.

Wrapper logic can affect input construction, entry-point selection, error handling, or result interpretation.

### `evaluated_at_utc`

Records when the decision was produced.

This timestamp is not evidence observation time.

### `decision_executed`

Records whether policy evaluation actually ran.

Blocked or invalid evidence must not be represented as an executed control decision.

### `result`

Records the output produced by the identified evaluation path.

The result is downstream of the evidence, transformation, context, policy artifact, engine, and implementation.

## Policy Change Is Not Target Drift

The prohibited shortcut is:

```text
PASS -> FAIL
=> target or control drift
```

when the policy also changed.

A safer interpretation is:

```text
same policy input
+ different policy semantics
-> different decision
-> policy difference must be resolved
-> target-state change is not established by the result difference alone
```

A policy change does not prove that the target did not change in a real environment.

It means the result difference alone is insufficient to attribute the change to the target.

## Policy Version Is Not Enough for Replay

A label such as:

```text
policy_version = 0.2.0
```

is useful but incomplete.

Replay also depends on the policy bytes, input bytes, evaluation context, decision entry point, engine behavior, and surrounding implementation.

The existing replayable TLS reference package already records SHA256 values for evidence, schemas, evaluation context, and policy, together with implementation and runtime versions.

This contract makes that policy-evaluation provenance boundary explicit rather than treating it as an incidental field in one replay package.

## Deterministic Evaluation Is Not Policy Correctness

OPA or another deterministic policy engine can reproduce the same output from the same inputs and policy artifact.

That does not establish that the policy encodes the correct control interpretation.

A policy can be deterministic and wrong.

A threshold can be inappropriate.

A rule can omit an exception.

A policy version can be approved for one scope and unsuitable for another.

Evaluation provenance answers:

```text
What policy path produced this result?
```

It does not automatically answer:

```text
Was this policy correct for the control?
```

That remains a separate governance and validation problem.

## Synthetic Example

See [`examples/policy-evaluation-provenance/`](../examples/policy-evaluation-provenance/).

The example holds one synthetic policy input constant by construction:

```text
days_to_expiry = 30
minimum_certificate_days_remaining = 30
```

Policy version `0.1.0` uses:

```text
days_to_expiry >= minimum_certificate_days_remaining
```

Its modeled expected result is `pass`.

Policy version `0.2.0` uses:

```text
days_to_expiry > minimum_certificate_days_remaining
```

Its modeled expected result is `fail`.

The target-state identifier, normalized fact, and evaluation context remain constant in the synthetic scenario.

Only the policy semantics change.

The example does not establish which policy is correct.

It shows one boundary:

```text
same policy input
+ different policy semantics
-> different decision
-> target-state change is not established by this difference alone
```

## Relationship to Existing Replay Artifacts

The replayable TLS control package already demonstrates a stronger bounded replay implementation:

```text
evidence schema gate
-> context schema gate
-> integrity gate
-> freshness gate
-> derived facts
-> decision evaluation
-> assessment result
```

It records policy and input-related digests and implementation/runtime provenance.

This contract does not replace that package.

It extracts one reusable architectural rule from it: a historical control result must remain bound to the policy and evaluation path that produced it.

## Current Implementation Boundary

This repository currently models policy-evaluation provenance through this contract, a synthetic comparison example, and the existing replayable TLS reference package.

The synthetic comparison does not execute OPA and its expected result files are not runtime captures.

The repository does not yet provide repo-wide policy-version equivalence testing.

It does not yet provide a generic cross-policy regression harness across evidence types.

It does not yet provide signed policy bundles or trusted policy-release attestation.

Those are separate implementation steps.

## Origin and Attribution

This artifact originates from **CodeYourCompliance**.

- Website: https://www.codeyourcompliance.com/
- GitHub organization: https://github.com/codeyourcompliance
- Original repository: https://github.com/codeyourcompliance/evidence-validation-pipeline

Attribution is requested for forks, references, adaptations, and discussions.

## Final Boundary

A control result is not independent of the policy that produced it.

If the policy artifact, input, context, engine, or implementation path disappears, part of the decision history disappears with it.
