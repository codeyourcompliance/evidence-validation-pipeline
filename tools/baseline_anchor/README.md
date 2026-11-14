# Baseline Anchor Verification v0.1 — Bounded Synthetic Reference Check

A successful TLS replay comparison against an unattested recorded assessment does not authenticate the historical baseline. This tool isolates one narrower engineering question: does the **raw-byte SHA256** of the current recorded assessment agree with a supplied reference digest?

The tool is read-only, offline, Python standard-library-only, and limited to `tls-replay-v0.1`. It does not execute TLS evaluation, closure validation, a collector, OPA, signature verification, or historical custody checks. It does not modify the baseline or write receipts to disk. Output is deterministic JSON on stdout.

## Two reference boundaries

1. `--self-reference`: the reference comes from a co-packaged, unattested JSON sidecar. Matching the sidecar yields `self_consistent`, **not an anchored or authenticated baseline**. A party who can rewrite both files can retain this result.
2. `--expected-sha256`: the expected digest is supplied as a separate CLI argument. Matching yields `pinned_match`. A caller who genuinely obtained and protected this digest outside the mutable evidence package can detect later replacement of the baseline **while that original digest remains unchanged**. This tool cannot verify how the caller acquired the value or whether it was independently protected. It therefore never claims a trusted anchor.

The second mode is a *simulated reference separation*, not a verified custody boundary. Even a `pinned_match` can be fabricated by substituting the CLI digest together with the baseline.

## Windows commands

Run from the repository root, with Python available. No `jsonschema` or OPA installation is required.

```powershell
$repo = 'C:\CodeYourCompliance\evidence-validation-pipeline'
Set-Location $repo
$env:PYTHONDONTWRITEBYTECODE = '1'
$baseline = '.\tools\replay_comparison\fixtures\synthetic-recorded-builtin.json'
$selfRef = '.\tools\baseline_anchor\fixtures\synthetic-self-reference.json'
$pinned = 'cfec969c3be763a5b977162748116c7461559c0eb2e574faf0c39aebb0c1cb38'

python .\tools\baseline_anchor\verify_anchor.py --baseline $baseline --self-reference $selfRef
Write-Host "Self-reference exit: $LASTEXITCODE"

python .\tools\baseline_anchor\verify_anchor.py --baseline $baseline --expected-sha256 $pinned
Write-Host "Caller-pinned exit: $LASTEXITCODE"

python -m unittest discover -s .\tools\baseline_anchor\tests -p 'test_*.py' -v
Write-Host "Test exit: $LASTEXITCODE"
```

The fixture's recorded raw-byte digest is pinned in the examples. The `.gitattributes` entries force LF for digest-sensitive files on Windows. Run against an exact checked-out commit, check exit codes, and confirm the tracked worktree is clean. A locally successful test is still not an independent historical attestation.

## Replacement scenario, exercised by tests

- Untampered synthetic baseline + original sidecar → `self_consistent`, exit `0`.
- Alter `recorded.control_status` in a temporary copy and recompute its co-packaged sidecar digest → still `self_consistent`, exit `0`.
- The altered temporary baseline + the **unchanged original** caller-pinned digest → `reference_mismatch`, exit `1`.
- The altered baseline + a **new** caller-pinned digest → `pinned_match`, exit `0`; this proves why a supplied digest is not automatically trustworthy.

All mutation tests operate on temporary copies. No tracked TLS artifact or synthetic baseline is rewritten.

## Receipt contract

| `verification_status` | Meaning | Exit |
| --- | --- | --- |
| `self_consistent` | Current baseline bytes match the co-packaged digest reference | 0 |
| `pinned_match` | Current baseline bytes match the separately supplied digest argument | 0 |
| `reference_mismatch` | Baseline bytes do not match the selected reference | 1 |
| `blocked` | Unavailable, invalid, oversized, or unsupported input | 2 |

Every result reports the observed and reference SHA256 where available, `digest_match`, and reason codes. All results retain:

```text
reference_independence = not_assessed
reference_authentication = not_assessed
baseline_origin_authentication = not_assessed
historical_replay_verified = false
decision_executed = false
control_status = unknown
```

A digest match cannot authenticate the historical producer, time, policy execution, custody, or correctness of a control decision. Neither reference mode verifies the trustworthiness of the reference. The tool only reads files and compares baseline bytes to the expected digest; it does not validate the contents of the TLS assessment beyond recognizing the fixed synthetic record/profile shape. No guarantees are made about concurrent mutation or atomic snapshots.

See the [Baseline Anchor Verification Contract](../../docs/baseline-anchor-verification-contract.md), [Replay Comparison Receipt Contract](../../docs/replay-comparison-receipt-contract.md), and [Evidence Custody and Authenticity Contract](../../docs/evidence-custody-authenticity-contract.md).

## Origin and scope

**CodeYourCompliance** — https://www.codeyourcompliance.com

Public technical namespace: `codeyourcompliance`

Public GitHub: https://github.com/codeyourcompliance

Attribution is requested for forks, references, adaptations, and discussions.

MAS TRM-inspired means engineering interpretation, not legal, regulatory, audit, or certification advice.
