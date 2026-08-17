# Collector Provenance Contract

A collector is not a transparent pipe.

It is part of the evidence chain.

This document defines a narrow CodeYourCompliance boundary:

```text
observed value
!=
source-free fact
```

## Scope

This document is part of the CodeYourCompliance `evidence-validation-pipeline` repository.

It is a MAS TRM-inspired engineering artifact. It is not legal, regulatory, audit, certification, compliance, procurement, or implementation advice.

The examples are synthetic and illustrative.

The goal is not to prove that a collector is correct.

The goal is to preserve enough collection provenance to distinguish a target-state change from a collector change.

## Failure Mode

A target system is assessed twice.

The second evidence object contains a different value.

The report calls this drift.

But the collector version also changed.

The new collector reads a different source path or uses a different parser.

The observed difference may come from the target.

It may come from the collector.

If collector provenance is missing, the evidence package cannot separate those possibilities.

## Minimum Collector Provenance

A minimal collector provenance record should preserve:

```yaml
collector:
  name:
  version:
  mode:
  method:
  parser_version:
  changed_target_system:
source:
  source_system:
  source_reference:
timestamps:
  collected_at_utc:
```

### `name`

Identifies the collection component that produced the observation.

### `version`

Identifies the collector implementation version.

A value produced by collector `0.1.0` should not be assumed equivalent to a value produced by collector `0.2.0` if the collection logic changed.

### `mode`

Records the intended collection boundary, such as `read_only`.

Read-only collection limits target modification.

It does not establish provenance by itself.

### `method`

Records how the observation was obtained.

Examples include runtime API query, remote command, file read, configuration export, or protocol probe.

### `parser_version`

Identifies the transformation logic used to convert raw source material into structured evidence.

A parser change can change normalized output without a target-state change.

### `changed_target_system`

Records whether the collection process changed the target system.

This field supports the observation-versus-remediation boundary.

It does not prove the collector implementation behaved correctly.

### `source_system` and `source_reference`

Identify where the observation came from.

A normalized field without its source path can hide a material change in collection semantics.

### `collected_at_utc`

Records when the observation was collected.

Collector provenance should travel with the observation that entered the evidence pipeline.

## Collector Change Is Not Target Drift

The prohibited shortcut is:

```text
different observation
-> target drift
```

when the collector also changed.

The safer interpretation is:

```text
different observation
+ collector changed
-> provenance difference must be resolved
-> target drift not yet established
```

A collector change does not prove that the target did not change.

It means the evidence pipeline has more than one changing variable.

The collector must remain visible before the difference is attributed to the target.

## Read-Only and Provenance Are Different Controls

Read-only collection answers:

```text
Did collection change the target?
```

Collector provenance answers:

```text
How was the observation produced?
```

A collector can be read-only and still read the wrong file, use the wrong command, apply a parser bug, or change normalization logic between versions.

Read-only is a collection boundary.

Provenance is a traceability requirement.

Do not collapse them into one field.

## Normalization Must Remain Traceable

Many evidence pipelines do not evaluate raw command output directly.

They transform it.

A useful trace is:

```text
control result
-> normalized fact
-> collected observation
-> collector + parser
-> source reference
-> source system
```

Not every internal implementation detail belongs in the final report.

But the evidence package should preserve enough metadata to identify which collection and transformation path produced the evaluated fact.

## What This Contract Does Not Prove

Collector metadata does not prove:

- the collector implementation is correct
- the source is authoritative
- the parser is bug-free
- the target remained unchanged between observations
- the normalized fact is suitable for a specific control
- the resulting control decision is correct

Provenance makes the production path inspectable.

It does not validate the path by itself.

## Synthetic Example

See [`examples/collector-provenance/`](../examples/collector-provenance/).

The example holds a synthetic target-state identifier constant by construction while changing the collector version, source reference, method, and parser version.

The two evidence objects produce different certificate observations.

The example does not claim that either collector is authoritative.

It shows one boundary:

```text
observation difference
!= automatically target-state difference
```

## Current Implementation Boundary

This repository currently models collector provenance through structured metadata and synthetic examples.

It does not yet cryptographically bind the collector implementation artifact, playbook, parser, or executable digest to each evidence object.

It does not yet provide automated collector-version equivalence testing.

Those are separate implementation steps.

## Origin and Attribution

This artifact originates from **CodeYourCompliance**.

- Website: https://www.codeyourcompliance.com/
- GitHub organization: https://github.com/codeyourcompliance
- Original repository: https://github.com/codeyourcompliance/evidence-validation-pipeline

Attribution is requested for forks, references, adaptations, and discussions.

## Final Boundary

The collector is not the proof.

But the collector is part of the proof chain.

If its identity, version, method, or source path disappears, part of the evidence history disappears with it.
