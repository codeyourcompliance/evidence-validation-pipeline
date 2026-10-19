# Evidence Revision Lineage Contract

Correcting evidence must not erase the object that supported an earlier decision.

A replacement file with a matching hash may be internally consistent while making the original assessment impossible to replay.

This CodeYourCompliance contract defines a narrow boundary:

```text
revised evidence != rewritten history
current evidence selection != historical evidence identity
```

## Scope

This is a MAS TRM-inspired engineering interpretation, not legal, regulatory, audit, certification, procurement, implementation, or compliance advice.

The contract concerns post-collection revision lineage: how evidence identities, versions, reason codes, original inputs, and evaluation references should survive a correction.

It does not decide whether a proposed correction is valid, approved, or suitable for any particular control. It does not implement immutable storage, an append-only event store, version authorization, or policy re-evaluation.

Examples are synthetic structure comparisons, not runnable professional assessment cases or executed evidence-pipeline results.

## Failure Mode

A collector obtains a source response and a transformation produces a normalized fact. A policy evaluation later references that fact.

A reviewer discovers that the transformation rule used the wrong semantics.

An operator opens the stored JSON, changes the normalized field, and computes a new SHA256 digest.

The updated JSON and updated digest agree.

But the original bytes, the old normalized value, and the transformation path originally consumed by the evaluation are no longer available from that evidence package.

The current bytes can be consistent. The historical decision can still be unreplayable.

This is not target-system drift. The observed raw source value may be unchanged. The evidence representation was corrected after the observation.

## Correction Is Not Collection or Remediation

Keep four actions separate:

- **Observation:** a collector obtains state from a source at a stated collection time.
- **Transformation:** a rule derives a normalized fact from that observation.
- **Evidence revision:** a later record changes or withdraws a previously represented fact or evidence assertion, while preserving the old identity.
- **Remediation:** an authorized action changes the target system. Revision of an evidence record is not remediation.

A corrected normalization of one old observation must not receive a new collection timestamp that suggests the target was observed again.

If the collector actually runs again, the new output is a new observation with separate provenance. It is not merely a retrospective correction of the old one.

## Versioned Evidence Identity

A stable logical observation reference may group related evidence versions, but each version needs its own identity and byte reference.

```text
logical_observation_ref: obs-001

evidence_version_v1 -> digest_v1
evidence_version_v2 -> digest_v2

revision_event -> {v1, digest_v1, v2, digest_v2}
```

The same original raw observation reference can be used by both versions. The normalized values and transformation versions may differ.

Do not silently update the object referenced by an older evaluation to point to the newest version.

A digest records identity relative to a reference. It does not establish who authorized the revision or whether the correction is factually right.

## Minimum Revision Lineage

A minimal evidence revision record can preserve:

```yaml
revision_event:
  event_id:
  event_type:
  logical_observation_ref:
  original_evidence_id:
  original_evidence_sha256:
  successor_evidence_id:
  successor_evidence_sha256:
  raw_observation_ref:
  reason_code:
  claimed_actor_ref:
  recorded_at_asserted_utc:
  event_authentication_status:
  authorization_status:
  affected_evaluation_refs:
  impact_assessment_status:
  reevaluation_status:
```

This is a model, not a repository-wide validated schema.

### Original evidence reference

Identify the exact version and digest that the historical evaluation consumed.

If the original bytes no longer exist, a recorded digest alone does not reconstruct the historical policy input.

A separate, independently retained copy could still make reconstruction possible; the synthetic in-place-replacement scenario models loss within the provided package only.

### Successor evidence reference

Use a distinct evidence version identity and digest for the corrected representation.

Preserve the same raw observation reference when the revision corrects its normalization rather than collecting a new target state.

The successor is not automatically authoritative or admissible.

### Reason and event authority

Record why a revision is proposed: for example, changed normalization semantics or discovered collection-scope error.

An asserted actor name and event timestamp are metadata, not independently authenticated revision authorization or trusted time.

If no independent approval or verification took place, preserve `authorization_status = not_established` and `event_authentication_status = not_established`.

See the existing [Evidence Time Provenance Contract](evidence-time-provenance-contract.md) and [Evidence Custody and Authenticity Contract](evidence-custody-authenticity-contract.md).

### Historical evaluation references

An earlier policy evaluation may already be bound to the original evidence version.

That binding must remain intact even if the original evidence is later superseded for future use.

A revision can identify affected evaluation references; that list is not itself a completed impact analysis or replay.

Keep impact assessment and re-evaluation status explicit.

## Supersession, Retraction, and New Observation

These are not interchangeable:

- **Supersession:** a successor version is proposed or accepted for a defined use without deleting the original historical version. Acceptance is a separate, explicit authority decision.
- **Retraction:** an earlier evidence claim is withdrawn or flagged as not suitable for use; there may be no replacement.
- **New observation:** a source is observed again at a different collection time, producing a new observation and its own provenance.

A retraction does not mean the underlying technical control automatically failed.

A proposed supersession does not mean a new policy evaluation was executed.

A correction event itself is not evidence that the proposed new fact is correct.

## Replay Has Two Questions

Historical replay asks:

```text
What exact evidence bytes, transformation, policy input,
policy artifact, and evaluation context produced the original result?
```

Reassessment after correction asks:

```text
Would a separate evaluation with the new version
and its declared policy context produce a different result?
```

These are different operations.

The original result should not be overwritten by the later answer. If a new evaluation occurs, it needs its own evaluation record and explicit links to the revised evidence.

A revision without an impact assessment must not silently mark affected results as reviewed.

## Synthetic Comparison

The [example folder](../examples/evidence-revision-lineage/) compares two modeled structures.

**In-place replacement:** the earlier normalized evidence version is overwritten. An old digest reference remains, but the original payload is missing from the modeled package. The old evaluation binding cannot be replayed from that package.

**Linked revision:** the example preserves distinct old and new normalized evidence records, both tied to the same raw observation reference, plus a claimed revision event and an affected evaluation reference. Authority, source correctness, and policy re-evaluation remain unverified or not executed.

The fixtures do not execute a collector, transformation, real SHA256 calculation, custody authentication, append-only storage enforcement, OPA/Rego policy, policy replay, or control evaluation.

Placeholder digests are deliberately not computed SHA256 values.

## Current Implementation Boundary

This repository models the revision lineage distinction only through this contract and synthetic JSON fixtures.

It does not implement:

- enforced immutable evidence storage or append-only revision-event persistence
- executed cryptographic verification of either modeled version
- authentication or authorization of a revision actor
- automatic determination that a proposed correction is valid
- automatic lookup of every policy result affected by revision
- policy re-evaluation or retroactive rewriting of past decisions
- conflict resolution for competing revisions
- a generic lifecycle or retention engine

## Origin and Attribution

This artifact originates from **CodeYourCompliance**.

- Website: https://www.codeyourcompliance.com/
- GitHub organization: https://github.com/codeyourcompliance
- Original repository: https://github.com/codeyourcompliance/evidence-validation-pipeline

Attribution is requested for forks, references, adaptations, and discussions.

MAS TRM-inspired means engineering interpretation, not legal, regulatory, audit, certification, procurement, implementation, or compliance advice.

## Final Boundary

Correction is not permission to mutate historical proof.

The previous evidence version and its evaluation binding must remain identifiable. Any later version needs its own provenance and review state.

If the original evidence disappears, a newly matching hash cannot restore its audit history.
