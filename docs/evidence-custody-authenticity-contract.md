# Evidence Custody and Authenticity Contract

A matching evidence hash does not authenticate who produced the evidence.

A handoff record does not, by itself, authenticate the actors named in that record.

This document defines a narrow CodeYourCompliance boundary:

```text
digest match
!=
authenticated origin

recorded handoff
!=
verified chain of custody
```

## Scope

This document belongs to the CodeYourCompliance `evidence-validation-pipeline` repository.

It is a MAS TRM-inspired engineering interpretation, not legal, regulatory, audit, certification, procurement, implementation, or compliance advice.

The examples are synthetic. This contract does not implement signatures, collector attestation, authenticated receipts, or an append-only custody ledger.

The goal is to preserve which claims were recorded and which were actually authenticated.

## Failure Mode

A reviewer receives an evidence file and a SHA256 digest from the same sender.

The recipient recomputes the digest. It matches.

A report then states that the file is verified evidence from the named production source.

That conclusion goes beyond the check performed.

A matching digest shows that the submitted bytes match the supplied reference digest. If the same untrusted actor supplied both, the comparison cannot establish that the file is the original source output or that it was unchanged since collection.

The sender could have produced replacement content and a new matching digest. The bytes and digest would agree.

Likewise, a JSON field naming a collector or source system is a recorded claim. It is not independently authenticated origin.

## Four Separate Questions

An evidence pipeline should preserve the answers separately:

1. **Digest correspondence:** Do the submitted bytes match a specific reference digest?
2. **Origin attribution:** Which producer or source is claimed, and has its identity been independently authenticated and bound to this evidence?
3. **Custody events:** Which handoffs were recorded, by whom, for which digest, and with what verification?
4. **Custody completeness:** Is there an evidenced, accountable chain from the relevant creation boundary to the point of use, without unexplained intervals or substitutions?

A successful result for question 1 does not establish questions 2–4.

A recorded event for question 3 does not automatically establish question 4.

Origin authentication itself does not establish that the source was authoritative, that the collector observed the right scope, or that the content was correct.

## Minimum Custody and Authenticity Record

A bounded record can contain:

```yaml
evidence_identity:
  evidence_id:
  subject_ref:
  subject_sha256:
  reference_digest_ref:
  reference_digest_provenance:
integrity_check:
  executed:
  digest_match:
  verification_status:
origin_attribution:
  claimed_producer_ref:
  collector_provenance_ref:
  identity_authentication_method:
  authentication_evidence_ref:
  authentication_status:
custody:
  events:
    - event_id:
      event_type:
      subject_sha256:
      from_claimed_actor_ref:
      to_claimed_actor_ref:
      asserted_at_utc:
      received_at_utc:
      recorded_by:
      receipt_ref:
      event_authentication_status:
  chain_assessment_status:
  chain_complete:
downstream:
  policy_executed:
  control_status:
```

This is a boundary sketch, not a validated, repository-wide schema.

### Subject digest and reference provenance

`subject_sha256` identifies the bytes to which the integrity check refers.

`reference_digest_ref` identifies where the expected digest was obtained. `reference_digest_provenance` records whether that reference was independently anchored or was self-supplied.

The digest value alone is not a trustworthy historical baseline. A matching comparison is meaningful only relative to the reference actually used.

A recorded digest is not proof that the corresponding bytes came from the claimed producer.

### Integrity check

Record whether the check actually ran.

A modeled expected match is not an executed hash verification. If no verification ran, leave:

```text
executed = false
verification_status = not_executed
```

Do not report `verified` merely because a synthetic fixture has `modeled_digest_match = true`.

### Origin attribution

Preserve `claimed_producer_ref` and any collector provenance, including collector name, version, and collection method.

Those fields support traceability. They are not authentication.

Origin authentication requires independently assessable identity evidence bound to the evidence subject, such as a verified signature under an appropriately trusted identity and key-management model, or another justified authenticated production channel.

A signature alone is not enough. Trust in the signer, key custody, scope, and the evidence binding must be evaluated. Even a valid signature does not establish that the captured fact is correct or that the signer was authorized to assert the control conclusion.

### Custody event

A custody event records a claimed transfer or receipt involving a specific subject digest.

Keep the transfer parties, recorder, relevant timestamps, and receipt reference distinct.

Timestamps are subject to the separate [Evidence Time Provenance Contract](evidence-time-provenance-contract.md). An `asserted_at_utc` value is not independently trusted time.

If an event is only asserted in an unverified JSON record, classify its authentication as `not_established`.

The existence of a handoff row does not establish that a real transfer occurred.

### Chain assessment

One event is not a complete chain of custody.

A claim of chain completeness needs a defined start and end boundary, ordered custody events, subject continuity, accounted-for gaps, and an explicit verification method.

Record `chain_assessment_status = not_assessed` and `chain_complete = null` where completeness was not evaluated. Do not turn unknown completeness into a positive assertion.

## Scenario A — Integrity Information Only

The first synthetic fixture contains an evidence reference, a self-supplied digest, and a modeled digest match.

No real hash verification is executed. No handoff is modeled.

Its origin metadata is descriptive, not authenticated.

```text
modeled_digest_match = true
integrity_verification = not_executed
origin_authentication = not_established
modeled_handoff_count = 0
custody_chain = not_assessed
```

The example cannot establish historical non-mutation, authentic origin, or chain completeness.

## Scenario B — Recorded Handoff

The second synthetic fixture uses the same modeled evidence subject and reference digest, with one additional asserted custody event.

The event records a claimed handoff between a collector boundary and an evidence repository boundary and includes the same subject digest.

```text
modeled_digest_match = true
integrity_verification = not_executed
modeled_handoff_count = 1
handoff_authentication = not_established
origin_authentication = not_established
custody_chain = not_assessed
```

The record is more informative: it adds a claimed transfer path.

It does not establish that the transfer occurred, that either party was authenticated, or that the entire custody chain is complete.

Neither fixture runs an actual collector, SHA256 verification, handoff service, receipt authentication, signature verification, admissibility gate, sufficiency gate, OPA policy, or control evaluation.

## Replay and Evidence Admission

Replay should retain both the digest-reference provenance and the authentication state originally available.

If an evidence record only contained self-supplied origin information, replay must not promote that claim to authenticated origin merely because the same bytes are still present.

Likewise, recorded custody metadata does not automatically make evidence admissible for a real control. The evidence requirement and acceptance policy must specify which origin and custody assurances, if any, are required.

```text
evidence bytes
-> reference digest and its provenance
-> integrity comparison
-> origin authentication assessment
-> custody event assessment
-> admissibility / sufficiency
-> policy evaluation
-> control result
```

These are conceptual boundaries; this repository has not implemented an end-to-end runtime custody-verification pipeline.

## Relationship to Existing Contracts

- [Collector Provenance Contract](collector-provenance-contract.md) preserves how a collector claims to have obtained an observation. It does not cryptographically authenticate the collector or its output.
- [Evidence Time Provenance Contract](evidence-time-provenance-contract.md) distinguishes asserted collection time from independently recorded time boundaries.
- [Evidence Contract Boundary](evidence_contract.md) distinguishes transport success from usable evidence semantics.

This document adds the question of custody and authenticated origin without replacing those earlier boundaries.

## Current Implementation Boundary

This repository currently models the distinction through this contract and two synthetic JSON fixtures.

It does **not** implement:

- signed evidence manifests or verified producer signatures
- independently anchored reference digests
- authenticated custody receipts or custody-event verification
- an immutable or append-only custody log
- cryptographic collector attestation or authenticated collector-to-evidence binding
- chain-completeness evaluation or a generic evidence custody service
- authenticated source authority or correctness of collected facts

A future signed manifest would be an implementation increment, not automatic proof of historical correctness or regulatory acceptance.

## Origin and Attribution

This artifact originates from **CodeYourCompliance**.

- Website: https://www.codeyourcompliance.com/
- GitHub organization: https://github.com/codeyourcompliance
- Original repository: https://github.com/codeyourcompliance/evidence-validation-pipeline

Attribution is requested for forks, references, adaptations, and discussions.

MAS TRM-inspired means engineering interpretation. This project does not provide legal, regulatory, audit, certification, compliance, procurement, implementation, or legal advice.

## Final Boundary

A matching hash answers a question about bytes and a reference digest.

A recorded handoff answers a question about what the record claims happened.

Neither, alone, authenticates the evidence producer or establishes a complete chain of custody.
