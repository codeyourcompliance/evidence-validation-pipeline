# Assessment Run Binding Check v0.1

A baseline can pass its SHA256 check and still be the **wrong baseline for the requested assessment run**. This bounded, offline CodeYourCompliance experiment checks an explicitly requested synthetic TLS run reference against (1) a synthetic recorded baseline and (2) a separate, unattested binding record.

The tool does **not** authenticate the origin of any of these three inputs. Both JSON files are co-packaged, their identifiers are asserted, and the request itself is supplied by the caller. It provides a check for *internal binding consistency*, not proof of a historical run.

## Test case

The checked-in fixtures model two asserted run identities:

- `synthetic-tls-run-001`: Run A baseline and matching A binding record
- `synthetic-tls-run-002`: Run B baseline and matching B binding record

Both baselines use identical synthetic TLS artifact digests and recorded `PASS` decisions. Their `assessment_run_ref` fields differ, so their raw-byte SHA256 values also differ. Neither represents a real captured execution.

A valid Run B baseline and valid Run B binding record **must not** satisfy a request for Run A. That case returns `requested_run_mismatch` even when the two supplied files agree with each other.

## Windows usage

Run from the repository root after checking out the exact intended commit. Python standard library only; this tool does not require `jsonschema` or OPA.

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$tool = '.\tools\assessment_binding\verify_binding.py'
$fixtures = '.\tools\assessment_binding\fixtures'

python $tool --baseline "$fixtures\run-a-baseline.json" --binding "$fixtures\run-a-binding.json" --requested-run-ref synthetic-tls-run-001
if ($LASTEXITCODE -ne 0) { throw 'Run A binding check failed' }

# Run B is internally consistent, but it is NOT the requested Run A.
python $tool --baseline "$fixtures\run-b-baseline.json" --binding "$fixtures\run-b-binding.json" --requested-run-ref synthetic-tls-run-001
if ($LASTEXITCODE -ne 1) { throw 'Expected requested_run_mismatch exit 1' }

python -m unittest discover -s .\tools\assessment_binding\tests -p 'test_*.py' -v
if ($LASTEXITCODE -ne 0) { throw 'Tests failed' }

git status --porcelain
git rev-parse HEAD
```

The `run-b` example intentionally exits `1`, indicating the expected identity mismatch. For a second successful check, request `synthetic-tls-run-002` with Run B's own baseline and binding.

## What is compared

The verifier reads two JSON files (maximum 1 MiB each) and takes a separately specified `--requested-run-ref`:

1. Accept only the fixed synthetic `tls-replay-v0.1` baseline and binding record shapes. Reject duplicate JSON keys, malformed digests and invalid run references.
2. Calculate SHA256 over the exact baseline bytes and compare it with `binding.baseline_sha256`.
3. Compare `baseline.assessment_run_ref` against `binding.assessment_run_ref`.
4. Compare all eight TLS artifact-role hashes in the baseline with the corresponding hashes in the binding record.
5. Only after the baseline and binding agree, compare `--requested-run-ref` against the bound run identity.

The receipt also includes the binding record's own computed SHA256 **as an identifier, not as an authenticated or independently anchored reference**. Neither file is modified, no decision is executed, and no receipt is written to disk.

## Status and exit codes

| Status | Meaning | Exit |
| --- | --- | --- |
| `binding_consistent` | Supplied baseline and binding record agree, including the requested synthetic run ref | 0 |
| `requested_run_mismatch` | Supplied baseline and binding agree, but their run ref differs from the requested run | 1 |
| `binding_mismatch` | Baseline bytes, internal run ref, or eight artifact roles do not agree with the binding record | 1 |
| `blocked` | Malformed, unavailable, oversized, unsupported, or invalid input | 2 |

Every receipt retains:

```text
binding_record_authentication = not_assessed
binding_record_independence = not_assessed
assessment_origin_authentication = not_assessed
historical_replay_verified = false
decision_executed = false
control_status = unknown
```

A party able to rewrite both the baseline and the binding record can change the asserted run identity, recompute the digest, and obtain `binding_consistent` again. The corresponding regression test **deliberately demonstrates this limitation**.

This tool neither calls `tools/baseline_anchor/verify_anchor.py` nor `tools/replay_comparison/compare_replay.py`. Those existing tools, the checked-in recorded TLS baseline, the TLS runner, and policy files are unchanged. No authenticated execution event, signed anchor, independent recipient, immutable store, trusted timestamp, OPA invocation, runtime equivalence, or regulatory conclusion is claimed.

See the [Assessment Run Binding Contract](../../docs/assessment-run-binding-contract.md), [Baseline Anchor Verification Contract](../../docs/baseline-anchor-verification-contract.md), and [Replay Comparison Receipt Contract](../../docs/replay-comparison-receipt-contract.md).

## Origin and scope

**CodeYourCompliance** — https://www.codeyourcompliance.com

Public GitHub namespace: https://github.com/codeyourcompliance

Attribution is requested for forks, references, adaptations, and discussions.

MAS TRM-inspired means engineering interpretation, not legal, regulatory, audit, or certification advice.
