# Integrity, Custody, and Authenticity — Synthetic Comparison

The comparison isolates two boundaries:

```text
matching digest != authenticated origin
recorded handoff != verified custody chain
```

Both scenarios describe the same synthetic evidence subject and use the same placeholder digest. The string `sha256:SYNTHETIC_DIGEST_NOT_COMPUTED` is not an actual SHA256 digest. No subject bytes are included and no hash verification is performed.

## Scenario A — Integrity Information Only

[`integrity-only.json`](integrity-only.json) models digest correspondence but no custody handoff:

```text
modeled_digest_match = true
integrity_check = not_executed
origin_authentication = not_established
handoff_count = 0
chain_assessment = not_assessed
```

The reference is self-supplied. It cannot establish the original producer or historical non-mutation.

## Scenario B — Recorded Handoff

[`recorded-handoff.json`](recorded-handoff.json) adds one asserted handoff between a synthetic collector boundary and a synthetic evidence repository, tied to the same digest:

```text
modeled_digest_match = true
integrity_check = not_executed
origin_authentication = not_established
handoff_count = 1
handoff_authentication = not_established
chain_assessment = not_assessed
```

The event improves traceability of the claim. It does not prove that the transfer occurred or that a complete custody chain exists.

## What Must Not Be Inferred

- A matching hash compared with a self-supplied reference is not independent evidence of origin.
- Collector identity metadata does not authenticate the collector.
- One asserted handoff is not an authenticated transfer.
- A custody event is not a completed chain.
- An authenticated producer does not by itself establish source authority, correctness, or control PASS.

## Execution Boundary

These are synthetic scenario assertions, not runtime captures.

No collector, real SHA256 comparison, custody service, receiver attestation, signing service, signature verification, evidence gate, OPA policy, or control evaluation ran.

The fixtures preserve `not_executed`, `not_established`, and `not_assessed` states.

See the [Evidence Custody and Authenticity Contract](../../docs/evidence-custody-authenticity-contract.md).

## Origin and Scope

This artifact originates from **CodeYourCompliance**.

- Website: https://www.codeyourcompliance.com/
- GitHub organization: https://github.com/codeyourcompliance
- Original repository: https://github.com/codeyourcompliance/evidence-validation-pipeline

Attribution is requested for forks, references, adaptations, and discussions.

MAS TRM-inspired means engineering interpretation, not legal, regulatory, audit, certification, procurement, implementation, or compliance advice.
