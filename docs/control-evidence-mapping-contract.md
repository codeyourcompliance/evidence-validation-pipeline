# Control-to-Evidence Mapping Contract

Valid evidence is not automatically sufficient evidence.

A control claim may depend on more than one required evidence type.

This document defines a narrow CodeYourCompliance boundary:

```text
admissible evidence objects
!=
sufficient evidence set
```

## Scope

This document is part of the CodeYourCompliance `evidence-validation-pipeline` repository.

It is a MAS TRM-inspired engineering artifact. It is not legal, regulatory, audit, certification, compliance, procurement, or implementation advice.

The examples are synthetic and illustrative.

The goal is not to define a complete control catalog.

The goal is to preserve the mapping between a control claim and the evidence requirements that must be satisfied before control evaluation is allowed.

## Failure Mode

A control requires two independent observations.

One evidence object is present, fresh, integrity-verified, and admissible.

The second required evidence object is missing.

A pipeline evaluates the control anyway because every evidence object it did receive is valid.

That conclusion is not supported by the declared evidence requirement set.

The problem is not evidence validity.

The problem is evidence sufficiency.

## Evidence Validity and Evidence Sufficiency Are Different Gates

Evidence admissibility asks whether an individual evidence object is usable.

Examples include:

- schema valid
- integrity verified
- freshness acceptable
- provenance present
- expected context available

Evidence sufficiency asks whether the required evidence set for the control has been assembled.

A control can therefore be in this state:

```text
all present evidence = admissible
required evidence set = incomplete
control decision = blocked
control status = unknown
```

The missing requirement does not become a failed control condition.

It remains a missing proof input.

## Minimum Control-to-Evidence Mapping

A minimal mapping should preserve:

```yaml
control_evidence_mapping:
  mapping_id:
  mapping_version:
  control_id:
  control_version:
  control_claim:
  evaluation_rule:
  evidence_requirements:
    - requirement_id:
      requirement_version:
      required:
      evidence_type:
      evidence_layer:
      minimum_objects:
      scope_ref:
      admissibility_required:
```

### `mapping_id` and `mapping_version`

Identify the evidence-requirement map used for the assessment.

A control can acquire or lose evidence requirements over time.

The mapping version must therefore survive with the assessment history.

### `control_id` and `control_version`

Identify the control claim the evidence set is intended to support.

A control label alone is not enough when the claim semantics change across versions.

### `control_claim`

States the bounded claim that the evidence set is intended to support.

The claim should be narrower than a framework heading or checklist category.

### `evaluation_rule`

States how requirement completeness is interpreted before downstream policy evaluation.

A common rule is:

```text
all required evidence requirements must be satisfied
```

This is an evidence-sufficiency rule.

It is not the downstream control policy itself.

### `requirement_id` and `requirement_version`

Identify each evidence requirement independently.

This allows an assessment to show which required proof input was present, missing, invalid, stale, or unresolved.

### `required`

Separates mandatory proof inputs from optional supporting artifacts.

Optional evidence may improve review context.

It must not silently become mandatory or substitute for a missing required object.

### `evidence_type` and `evidence_layer`

Define what kind of evidence can satisfy the requirement and at which evidence layer.

A report should not silently substitute for raw or normalized evidence if the requirement expects a lower-layer proof object.

### `minimum_objects`

Defines the minimum number of admissible evidence objects required for that requirement.

This field does not prove scope completeness by itself.

Scope semantics remain separate.

### `scope_ref`

Links the requirement to the target or declared scope it is expected to cover.

A valid evidence object from the wrong scope does not satisfy the intended requirement.

### `admissibility_required`

States whether evidence must pass the evidence admissibility gate before it can satisfy the requirement.

For control evaluation, the default should be explicit rather than assumed.

## Missing Evidence Is Not a Failed Control

The prohibited shortcut is:

```text
required evidence missing
=> control failed
```

The missing object was not evaluated.

A safer state is:

```text
required evidence missing
-> evidence set incomplete
-> control evaluation blocked
-> control status unknown
```

This preserves the difference between proof absence and proof of failure.

## Admissible Evidence Can Still Be Insufficient

Suppose a synthetic TLS control requires both:

1. certificate-state evidence
2. runtime protocol-state evidence

The certificate evidence is present and admissible.

The runtime protocol evidence is absent.

The evidence set is incomplete even though the only evidence object present is valid.

The distinction is:

```text
present evidence quality = acceptable
required evidence coverage = incomplete
```

A pipeline that checks only evidence quality can still manufacture a control conclusion from an incomplete proof set.

## Mapping Version Is Part of Replay

Historical replay needs the evidence requirement map as well as the evidence and policy artifacts.

If a later mapping introduces a second required evidence type, replaying an older assessment against the new mapping answers a different question.

The historical path is closer to:

```text
control claim
-> evidence requirement map
-> admissible evidence set
-> policy input
-> policy evaluation
-> control result
```

The mapping sits before policy evaluation.

It defines what evidence is required before the policy is allowed to run.

## Mapping Completeness Is Not Control Correctness

A complete evidence set can still support the wrong control design.

The mapping may omit an important requirement.

An evidence type may be inappropriate.

The declared scope may be too narrow.

A requirement may be mapped to the wrong source.

Control-to-evidence mapping answers:

```text
Did the declared evidence requirements get satisfied?
```

It does not automatically answer:

```text
Were these the correct evidence requirements for the control?
```

That remains a separate control-design and review problem.

## Synthetic Example

See [`examples/control-evidence-mapping/`](../examples/control-evidence-mapping/).

The synthetic control requires two evidence types:

```text
tls_certificate_state
tls_runtime_protocol_state
```

The complete example satisfies both requirements with admissible evidence references and allows downstream policy evaluation.

The incomplete example satisfies only the certificate-state requirement.

Its state is:

```text
evidence_set_status = incomplete
policy_evaluation_allowed = false
control_status = unknown
```

No control failure is manufactured from the missing protocol evidence.

## Relationship to Existing Artifacts

The evidence admissibility gate determines whether an individual evidence object is usable.

The collector, transformation, and policy-evaluation provenance contracts preserve how observations, normalized facts, and decisions were produced.

This contract adds a different boundary: whether the declared set of required proof inputs exists before policy evaluation begins.

It does not replace object-level admissibility or downstream policy logic.

## Current Implementation Boundary

This repository currently models control-to-evidence mapping through this contract and synthetic examples.

It does not yet implement repo-wide evidence requirement schema enforcement.

It does not yet implement automatic evidence-set assembly across evidence types.

It does not yet implement control-catalog version governance or cryptographic binding of mapping artifacts to assessment results.

It does not yet prove that a declared evidence requirement map is complete or correct for a real control.

Those are separate implementation steps.

## Origin and Attribution

This artifact originates from **CodeYourCompliance**.

- Website: https://www.codeyourcompliance.com/
- GitHub organization: https://github.com/codeyourcompliance
- Original repository: https://github.com/codeyourcompliance/evidence-validation-pipeline

Attribution is requested for forks, references, adaptations, and discussions.

## Final Boundary

Evidence quality and evidence sufficiency are different gates.

If a required proof input is missing, the control has not been proven to pass or fail.

The missing state must survive.
