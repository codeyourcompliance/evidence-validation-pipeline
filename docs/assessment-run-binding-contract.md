# Assessment Run Binding Contract v0.1

## Failure mode

A reviewer asks for assessment Run A. The system returns a different baseline from Run B along with Run B's correctly matching digest and binding record. A SHA256 check succeeds, but the selected evidence belongs to the wrong asserted run identity.

A valid digest answers which bytes were checked against which reference; it does not answer whether those bytes belong to **the assessment requested by the reviewer**.

This CodeYourCompliance experiment separates digest correspondence from *assessment identity binding*. It uses a MAS TRM-inspired engineering interpretation; this contract is not legal, regulatory, audit, certification, or compliance advice.

## Scope and fixture identity

Two new synthetic baseline fixtures derive from the existing unattested `tls-replay-v0.1` recorded assessment, without changing the original fixture or the existing replay/anchor tools. The only intentionally distinct semantic field is the synthetic `assessment_run_ref`:

```text
Run A: synthetic-tls-run-001
Run B: synthetic-tls-run-002
```

Both have identical eight TLS artifact role digests, builtin decision-engine metadata, and recorded `PASS` outcomes. They are **not** two captured production runs or two verified historic executions. Their differing asserted run refs make their raw-byte SHA256 values different.

Each baseline is accompanied by an **unattested co-packaged binding record** containing:

```yaml
record_type: synthetic_tls_assessment_run_binding_v0.1
profile: tls-replay-v0.1
reference_origin: co_packaged_unattested
assessment_run_ref: synthetic-tls-run-001
baseline_sha256: <digest of the exact baseline bytes>
artifact_sha256:
  evidence: <digest>
  evidence_digest: <digest>
  evidence_schema: <digest>
  evaluation_context: <digest>
  context_schema: <digest>
  policy: <digest>
  replay_implementation: <digest>
  runtime_requirements: <digest>
```

This describes a proposed `assessment_run_ref -> baseline digest -> binding record` relationship. The tool does **not** independently establish the relationship's origin, history, or authority. In particular, it does not check that a run really executed. The caller supplies the expected run identity as another assertion; no authenticated external run registry is consulted.

## Bounded checks

The verifier accepts `--baseline`, `--binding` and `--requested-run-ref`.

It parses both JSON files with duplicate-key rejection, bounds file sizes, validates fixed synthetic record shapes, and compares:

1. actual baseline raw-byte SHA256 to `binding.baseline_sha256`;
2. baseline `assessment_run_ref` to binding `assessment_run_ref`;
3. all eight artifact role SHA256 fields between baseline and binding;
4. the requested run reference to the mutually consistent baseline/binding run reference.

The requested run comparison occurs only after the internal binding checks, so an internally inconsistent pair is not misclassified as a valid record belonging to another run. It emits deterministic JSON to stdout and does not change evidence, emit trusted time, execute a policy, or determine control pass/fail.

## Receipt and status semantics

```yaml
receipt_version: 0.1.0
profile: tls-replay-v0.1
verification_status: binding_consistent | requested_run_mismatch | binding_mismatch | blocked
requested_assessment_run_ref: string | null
baseline_assessment_run_ref: string | null
binding_assessment_run_ref: string | null
baseline_sha256: string | null
reference_baseline_sha256: string | null
binding_record_sha256: string | null
baseline_digest_match: true | false | null
artifact_bindings_match: true | false | null
reason_codes: []
binding_record_authentication: not_assessed
binding_record_independence: not_assessed
assessment_origin_authentication: not_assessed
historical_replay_verified: false
decision_executed: false
control_status: unknown
```

`binding_consistent` exits `0`. Both mismatch statuses exit `1`. Unavailable, oversized, invalid, and unsupported inputs return `blocked` with exit `2`. A requested-run mismatch is **not** control failure, evidence collection failure, or established target drift.

## Synthetic comparison results

| Supplied baseline | Supplied binding | Requested run | Result |
| --- | --- | --- | --- |
| Run A | Run A | A | `binding_consistent` |
| Run B | Run B | B | `binding_consistent` |
| Run B | Run B | A | `requested_run_mismatch`, even though both hashes are valid |
| Run B | Run A | A | `binding_mismatch` |
| Relabeled Run B plus matching rewritten binding | Rewritten | A | `binding_consistent`, **not authenticated** |

The last test makes the limitation explicit: an actor who can rewrite both files can invent a new internally consistent identity binding. This implementation does not detect that actor or prove the asserted identity existed at the original run time.

## What remains unverified

- Assessment run IDs are synthetic labels, not authenticated IDs from an execution service.
- The binding record is supplied alongside the baseline and is not signed, externally anchored, or retained under independently verified custody.
- The baseline's artifact digests are **compared as claims**; this tool does not reopen all eight artifact files, rerun closure, or re-execute the TLS assessment.
- SHA256 over a binding record does not authenticate its issuer or historical timestamp.
- No policy correctness, OPA execution, evaluation authorization, runtime equivalence, or historical assessment authenticity is established.

The [Replay Comparison Receipt Contract](replay-comparison-receipt-contract.md) governs current-run comparisons against supplied synthetic baseline fields. The [Baseline Anchor Verification Contract](baseline-anchor-verification-contract.md) governs baseline digest correspondence to supplied references. The [Evidence Custody and Authenticity Contract](evidence-custody-authenticity-contract.md) describes the separate problems of issuer authentication, reference provenance and custody continuity.

This v0.1 verifier does not combine those tools into a trustworthy end-to-end historical replay system. An independent execution event register and authenticated custody for baseline and binding records would require a separate implementation and validation.

## Origin and attribution

This artifact originates from **CodeYourCompliance**.

Website: https://www.codeyourcompliance.com

GitHub: https://github.com/codeyourcompliance

Attribution is requested for forks, references, adaptations and discussions.

MAS TRM-inspired means engineering interpretation, not legal, regulatory, audit, or certification advice.

## Final boundary

A pinned digest does not identify the run unless the baseline-to-run relationship is verified. An internally consistent synthetic run binding is not an authenticated historical execution.
