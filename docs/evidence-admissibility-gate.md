# Evidence Admissibility Gate

This document defines the current evidence-admissibility boundary implemented by the `evidence-validation-pipeline` reference examples.

The rule is simple:

```text
Evidence must pass admissibility checks before a control decision may execute.
```

Invalid evidence is not a failed control.

Stale evidence is not a failed control.

Invalid evaluation context is not a failed control.

If an admissibility gate fails, the control decision remains unknown because it was not executed.

This is a CodeYourCompliance engineering interpretation. MAS TRM-inspired does not mean legal, regulatory, audit, certification, procurement, or prescribed implementation advice.

## Why the gate exists

A collector, parser, integrity check, freshness check, or evaluation context can fail before the control itself is evaluated.

If those failures are compressed into `fail`, the result no longer distinguishes two different events:

```text
control condition failed
```

from:

```text
evidence or context could not support a control decision
```

That distinction must survive the pipeline.

## Current reference pipeline

The bounded replayable TLS example implements this sequence:

```text
evidence schema gate
-> context schema gate
-> integrity gate
-> freshness gate
-> derived facts
-> decision evaluation
-> assessment result
```

Decision evaluation occurs only after the preceding gates pass.

The implementation is in:

```text
examples/replayable-tls-control/replay.py
```

## Current state contract

The current replayable TLS reference package uses these states:

| Evidence/context state | Decision evaluation | Control status | Meaning |
| --- | --- | --- | --- |
| `valid` evidence + `valid` context | allowed | `pass` or `fail` | admissible inputs reached the control decision |
| `invalid_evidence` | blocked | `unknown` | evidence schema or integrity gate failed |
| `stale_evidence` | blocked | `unknown` | evidence failed the freshness gate |
| `invalid_context` | blocked | `unknown` | evaluation context schema gate failed |

The invariant is:

```text
decision_executed = false
=> control_status = unknown
```

A blocked decision must not be rewritten as a failed control.

## Evidence evaluation is not control evaluation

The repository also contains a narrow Rego demo for evidence freshness:

```text
policies/demo/evidence_freshness.rego
```

That policy evaluates whether evidence is fresh enough to proceed.

It is an admissibility policy.

It is not the downstream control decision.

The distinction is:

```text
evidence admissibility evaluation
!=
control decision evaluation
```

An admissibility policy may classify an evidence object as stale and block downstream evaluation.

That does not mean the control itself evaluated to `fail`.

## Existing examples

### Integrity failure

`examples/invalid_evidence_result.json` records a hash mismatch and explicitly sets policy execution to false.

The evidence failed before policy evaluation.

### Replay result with invalid evidence

`examples/replayable-tls-control/expected/invalid_evidence.json` records:

```text
evidence_status = invalid_evidence
control_status = unknown
decision_executed = false
```

This is the reference state separation.

### Valid evidence

`examples/replayable-tls-control/expected/pass.json` demonstrates the opposite path: admissible evidence reaches decision evaluation and produces a control result.

### Stale evidence

`examples/stale_evidence.json` demonstrates evidence that passes integrity verification but is outside its declared freshness window.

The freshness classification belongs to evidence admissibility. It does not create a failed control result.

## Scope boundary

This document describes the states currently represented by the public reference implementation.

It does not claim that the repository already implements a complete evidence-state taxonomy.

Potential states such as `missing_evidence` or `unsupported_evidence` require their own explicit semantics before they should be added to this contract.

Do not infer a control result from an unimplemented or ambiguous evidence state.

## Implementation rule

```text
No admissible evidence.
No control decision.
```

The control result starts only after the evidence has passed the gate.
