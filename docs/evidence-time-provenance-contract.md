# Evidence Time Provenance Contract

A timestamp field is not proof of when evidence existed.

An evidence object can contain a syntactically valid UTC timestamp and still leave the time claim entirely dependent on the collector clock.

This document defines a narrow CodeYourCompliance boundary:

```text
timestamp value
!=
time provenance
```

## Scope

This document is part of the CodeYourCompliance `evidence-validation-pipeline` repository.

It is a MAS TRM-inspired engineering artifact. It is not legal, regulatory, audit, certification, compliance, procurement, or implementation advice.

The examples are synthetic.

The goal is not to implement trusted timestamping.

The goal is to preserve enough time provenance to distinguish a collector-asserted timestamp from an independently recorded time boundary.

## Failure Mode

A collector creates an evidence object containing:

```json
"collected_at_utc": "2026-09-22T01:00:00Z"
```

The evidence object is then hashed with SHA256.

Later verification confirms that the stored object matches the stored hash.

That proves an integrity relationship between the current bytes and the recorded digest.

It does not prove that the collector actually observed the source at 01:00 UTC.

If the collector clock was wrong, the timestamp can be wrong.

If an operator created the object later with a backdated timestamp and then computed a new hash, the hash can still verify.

The time claim therefore needs its own provenance.

## Time Statements Answer Different Questions

An evidence pipeline may contain several different time values:

```text
source_event_time
collection_time
seal_time
receipt_time
trusted_attestation_time
```

They should not be treated as interchangeable.

### Source event time

A timestamp emitted by the source system.

It says when the source claims an event occurred.

Its trust depends on the source clock and event semantics.

### Collection time

A timestamp recorded by the collector.

It says when the collector claims the observation occurred.

It does not independently prove that time.

### Seal time

A timestamp recorded when evidence bytes were hashed or packaged.

It says when the sealing process claims it ran.

The hash binds bytes. It does not by itself validate the clock.

### Receipt time

A timestamp recorded by a separate receiving system when it receives a specific evidence digest or package.

Under the stated receiver assumptions, it can establish a useful boundary:

```text
evidence existed no later than receipt_time
```

It still does not prove the exact collection time.

### Trusted attestation time

A time assertion bound to the evidence digest by an independently trusted timestamping mechanism.

This repository does not currently implement that mechanism.

The field belongs in the model so a collector timestamp is not silently treated as equivalent to a trusted timestamp.

## Minimum Time Provenance

A minimal time-provenance structure can preserve:

```yaml
time_provenance:
  collection_time:
    value_utc:
    asserted_by:
    clock_source_ref:
    assurance:
  seal_time:
    value_utc:
    asserted_by:
    subject_sha256:
    assurance:
  receipt_time:
    present:
    value_utc:
    recorded_by:
    subject_sha256:
    assurance:
  trusted_timestamp:
    present:
    authority_ref:
    token_ref:
    attested_at_utc:
    subject_sha256:
    verification_status:
```

### `collection_time`

Preserves the time the collector claims the observation occurred.

For a local collector clock, a suitable assurance label is:

```text
collector_asserted
```

### `clock_source_ref`

Identifies the clock source relied on by the asserting component.

Examples may include local system clock, NTP-synchronized host clock, source-system clock, or an externally provided time source.

Recording the clock source does not prove the clock was correct.

It makes the dependency visible.

### `seal_time`

Records when the sealing process claims the evidence digest was created.

The `subject_sha256` should identify the bytes that were sealed.

A seal time without independent time attestation remains asserted time.

### `receipt_time`

Records an independent receiving boundary when a separate system receives the evidence digest or package.

The receipt should bind to the same subject digest.

A receiver-recorded time can strengthen the evidence chain without being misrepresented as trusted timestamping.

### `trusted_timestamp`

Reserves fields for a cryptographically bound, independently attested time statement.

If trusted timestamping is not implemented, the correct state is:

```text
present = false
verification_status = not_implemented
```

The pipeline should not infer trusted time from a populated `collected_at_utc` field.

## Hash Integrity Is Not Time Integrity

The boundary is:

```text
hash verifies
=> stored bytes match recorded digest
```

It is not:

```text
hash verifies
=> embedded timestamp is historically true
```

A valid hash can protect a false timestamp just as effectively as a true one.

Hashing protects the representation after sealing.

It does not establish when the represented observation occurred.

## Independent Receipt Creates a Different Claim

Suppose a collector claims:

```text
collected_at_utc = 01:00
```

A separate evidence receiver records the digest at:

```text
received_at_utc = 01:03
```

If the receiver and its clock are accepted for the stated use, the receipt can support:

```text
this evidence digest existed by 01:03
```

It does not automatically prove:

```text
the target was observed at exactly 01:00
```

Those are different claims.

## Relationship to Freshness

Freshness evaluation depends on time.

For example:

```text
evaluation_time - collected_at <= allowed_age
```

That calculation may be deterministic while the underlying collection time remains only collector-asserted.

Therefore:

```text
freshness calculation correctness
!=
time assertion trust
```

A freshness gate should be able to disclose which time source it relied on.

## Relationship to Replay

Replay should preserve the original time semantics.

If an assessment originally relied on collector-asserted time, replay should not later present that timestamp as independently attested.

Likewise, if an independent receipt or trusted timestamp existed, the binding to the original evidence digest should survive replay.

The historical path is therefore closer to:

```text
observation
-> asserted collection time
-> evidence bytes
-> integrity seal
-> optional independent receipt / time attestation
-> admissibility
-> sufficiency
-> policy evaluation
-> result
```

Changing the time-assurance interpretation changes the evidence claim being replayed.

## Synthetic Examples

See `examples/evidence-time-provenance/`.

The examples compare:

1. evidence containing collector-asserted collection and seal times only; and
2. the same modeled evidence digest with a separately recorded receipt boundary.

Neither example executes a collector, trusted timestamp authority, signature verification, admissibility gate, OPA policy, or control evaluation.

The recorded states are synthetic scenario assertions.

## Current Implementation Boundary

This repository currently models time provenance only through this contract and synthetic examples.

It does not implement trusted timestamping.

It does not validate NTP synchronization or host clock correctness.

It does not cryptographically authenticate the receiver.

It does not issue or verify RFC 3161 timestamp tokens.

It does not prove that source-event time, collection time, receipt time, or attestation time are equivalent.

Those remain separate implementation steps.

## Origin and Attribution

This artifact originates from **CodeYourCompliance**.

- Website: https://www.codeyourcompliance.com/
- GitHub organization: https://github.com/codeyourcompliance
- Original repository: https://github.com/codeyourcompliance/evidence-validation-pipeline

Attribution is requested for forks, references, adaptations, and discussions.

## Final Boundary

A timestamp can record a claim about time.

Time provenance records why that claim should be trusted.

Those are not the same thing.
