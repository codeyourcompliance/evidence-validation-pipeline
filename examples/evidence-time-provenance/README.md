# Evidence Time Provenance

This synthetic example isolates one boundary:

```text
timestamp value
!=
time provenance
```

Both scenarios use the same synthetic evidence digest.

## Files

- `collector-asserted-time.json`
- `independent-receipt-time.json`

## Scenario A — Collector-Asserted Time

The evidence object contains collection and seal timestamps.

Both times are asserted by the collection pipeline.

The modeled state is:

```text
collection_time_assurance = collector_asserted
seal_time_assurance = collector_asserted
independent_receipt_present = false
trusted_timestamp_present = false
```

The evidence can still be integrity-checked.

The example does not claim that the timestamp itself was independently verified.

## Scenario B — Independent Receipt Boundary

The same synthetic evidence digest is modeled as being received by a separate evidence receiver.

The receiver records:

```text
received_at_utc = 2026-09-22T01:03:00Z
subject_sha256 = sha256:SYNTHETIC_EVIDENCE_DIGEST
```

Under the stated synthetic assumptions, this supports the narrower claim:

```text
the evidence digest existed no later than the recorded receipt time
```

It does not prove the exact collection time.

It is not modeled as a trusted timestamp authority.

## Scenario Assumptions

The independent-receipt scenario assumes, by construction, that:

- the receiver is separate from the collector
- the receiver records the digest it actually received
- the receiver clock is acceptable for the synthetic scenario
- the digest identifies the same evidence bytes

These are scenario assumptions, not runtime validations.

## Execution Boundary

These files are synthetic scenario models.

No real collector, receiver, timestamp authority, signature verifier, evidence-admissibility gate, OPA policy, or control evaluation is executed.

The examples do not implement trusted timestamping.

## What the Example Shows

The useful boundary is:

```text
collected_at_utc present
+ SHA256 verifies
-> integrity relationship exists
-> collection time may still be collector-asserted
```

and:

```text
same evidence digest
+ independent receipt time
-> separate time boundary exists
-> exact collection time still not independently proven
```

## What the Example Does Not Show

It does not prove host clock correctness.

It does not prove NTP synchronization.

It does not implement RFC 3161 or another trusted timestamp protocol.

It does not prove source authenticity.

It does not establish control pass.

## Origin and Scope

This artifact originates from **CodeYourCompliance**.

- Website: https://www.codeyourcompliance.com/
- GitHub organization: https://github.com/codeyourcompliance
- Original repository: https://github.com/codeyourcompliance/evidence-validation-pipeline

Attribution is requested for forks, references, adaptations, and discussions.

MAS TRM-inspired means engineering interpretation. This example does not provide legal, regulatory, audit, certification, compliance, procurement, or implementation advice.
