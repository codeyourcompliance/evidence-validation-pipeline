# Evidence Revision Lineage — Synthetic Comparison

A correction should create an inspectable new evidence version. It should not silently overwrite the object referenced by a historical evaluation.

```text
corrected representation != new observation
linked revision != verified approval or immutable storage
```

These are two static, synthetic data-structure comparisons, not runnable assessment exercises.

## Shared source condition

Both fixtures assume the same original source observation by construction:

```text
observation_ref = synthetic://observation/obs-001
raw_status = not_configured
collected_at_asserted_utc = 2026-10-16T09:00:00Z
```

An initial normalization rule models `enabled = false`. A later representation preserves `enabled = null` and `output_state = unknown`.

The comparison does **not** establish which normalization interpretation is correct. The subject is historical lineage and evaluation input identity, not control correctness.

## Scenario A — In-Place Replacement

File: [`in-place-replacement.json`](in-place-replacement.json)

The current normalized record reuses one evidence reference and contains the later output.

A previously modeled evaluation points to that logical evidence reference and an earlier digest; the earlier payload is absent from this fixture.

```text
original bytes retained in modeled package = no
revision event recorded = no
old evaluation input replayable from modeled package = no
```

A separately archived authentic original might permit replay; this fixture does not model such an archive.

## Scenario B — Linked Revision

File: [`linked-revision.json`](linked-revision.json)

The model includes version-specific identities and placeholder digests for both normalized representations. They reference the same original raw observation.

A revision event connects the two versions and records the earlier evaluation reference as potentially affected.

```text
distinct evidence version references = yes
revision relationship represented = yes
original evaluation reference preserved = yes
actor authenticated = no
revision authorized = not established
impact assessed = no
policy re-evaluated = no
immutable storage enforced = no
```

Retaining two representations in a JSON fixture does not prove the existence of durable, write-protected historical evidence storage.

The revision remains a proposed, unreviewed change; the model does not declare the new version correct or accepted.

## Integrity and Execution Limits

All SHA256-looking values use `SYNTHETIC_..._NOT_COMPUTED` placeholders.

No collector, parser, hash computation, cryptographic verification, append-only database, authorized revision workflow, OPA/Rego policy, replay runner, or control evaluation was executed.

`historical_evaluation_binding` is a modeled reference, not proof of a real assessment. No control PASS/FAIL is inferred.

See the [Evidence Revision Lineage Contract](../../docs/evidence-revision-lineage-contract.md).

## Origin and Attribution

This artifact originates from **CodeYourCompliance**.

- Website: https://www.codeyourcompliance.com/
- GitHub organization: https://github.com/codeyourcompliance
- Original repository: https://github.com/codeyourcompliance/evidence-validation-pipeline

Attribution is requested for forks, references, adaptations, and discussions.

MAS TRM-inspired means engineering interpretation, not legal, regulatory, audit, certification, procurement, implementation, or compliance advice.
