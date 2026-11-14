# Baseline Anchor Verification Contract v0.1

## Failure mode

A reviewer has an old TLS recorded assessment and a successful Replay Comparison Receipt. The evidence, manifest, and recorded baseline all agree. A later operator, however, could replace the recorded baseline and recompute its digest, leaving a package that is internally consistent without being the historical record.

The existing `tools/replay_comparison/` compares a **current** execution to an explicitly unattested synthetic reference. It never sets `historical_replay_verified = true`. This separate contract tests the digest-reference boundary, not the policy evaluation path.

## What is compared

The read-only comparator accepts the existing `tools/replay_comparison/fixtures/synthetic-recorded-builtin.json` as its fixed TLS synthetic subject and computes SHA256 over the **raw bytes** of that file. It checks one of two independently selected reference *locations*:

- `self_supplied_sidecar`: a separate JSON digest file packaged with the synthetic baseline. This reference is explicitly marked `co_packaged_unattested`.
- `operator_pinned_digest`: a lower-case SHA256 supplied through a CLI argument. The value may have been retained in another trust boundary, but this tool has no basis to authenticate its source or custody.

The implementation does not accept an "independently authenticated" mode or a caller-controlled `trusted=true` flag. It performs digest correspondence, not reference authentication. The selected reference can be changed by the caller; therefore neither `self_consistent` nor `pinned_match` is an independent authenticity verdict.

## Bounded deterministic receipt

```yaml
receipt_version: 0.1.0
profile: tls-replay-v0.1
reference_mode: self_supplied_sidecar | operator_pinned_digest
baseline_sha256: string | null
reference_sha256: string | null
digest_match: true | false | null
verification_status: self_consistent | pinned_match | reference_mismatch | blocked
reason_codes: []
reference_independence: not_assessed
reference_authentication: not_assessed
baseline_origin_authentication: not_assessed
historical_replay_verified: false
decision_executed: false
control_status: unknown
```

A match exits `0`; a mismatch exits `1`; blocked/invalid input exits `2`. The receipt is emitted only to stdout without wall-clock assertions, local host paths, or mutation of the evidence package. The tool refuses duplicate JSON keys and unsupported fixed-profile records, and bounds input file sizes.

`self_consistent` asserts only that current bytes match a digest placed next to the current bytes. `pinned_match` asserts that current bytes match the digest the caller supplied *for this invocation*. Neither status permits a stronger label such as `anchor_authenticated`, `historical_replay_verified`, `control_pass`, or `policy_executed`.

## Synthetic replacement test

1. Start with the existing unattested TLS baseline and its self-supplied digest. They match.
2. Modify the control-result field in a temporary copy; calculate a fresh sidecar digest. The new pair also matches. Its history has not been authenticated.
3. Compare the modified bytes against the **unchanged** original pinned digest. The check returns `reference_mismatch`.
4. Replace the pinned digest as well. The digest check returns `pinned_match` again. This demonstrates why a caller-provided hash, without validated provenance, is not an independently secured anchor.

This tests tamper **detection relative to a fixed reference**. It does not test a malicious actor's access controls, real independent custody, time stamping, a signature, append-only storage, or authorized issuance of a baseline.

## Implementation boundary

- Python standard library, offline, read-only. One synthetic `tls-replay-v0.1` recorded-baseline profile.
- No TLS evidence collection, runtime TLS evaluation, OPA execution, replay-runner invocation, schema policy validation, historical-source authentication, or runtime equivalence testing.
- Existing Replay Comparison Receipt and TLS source files remain unchanged.
- Unit tests execute isolated temporary file mutation scenarios. They establish comparator behavior, not independent baseline authenticity.
- An out-of-band digest is useful only under an explicit assumption that its recording, storage, distribution, and retrieval are protected from the actor changing the baseline. This comparator does not enforce that assumption.

The existing [Evidence Custody and Authenticity Contract](evidence-custody-authenticity-contract.md) models digest-reference provenance and verified custody as distinct questions. The [Evidence Time Provenance Contract](evidence-time-provenance-contract.md) separates asserted collection time from independently evidenced time. This experiment implements neither custody authentication nor trusted timestamping.

## Origin and scope

This artifact originates from **CodeYourCompliance**.

Website: https://www.codeyourcompliance.com

GitHub: https://github.com/codeyourcompliance

Attribution is requested for forks, references, adaptations, and discussions.

MAS TRM-inspired means engineering interpretation, not legal, regulatory, audit, or certification advice.

## Final boundary

A fixed reference digest can reveal a changed baseline. It cannot prove the reference itself was authentic, independent, or historically preserved.
