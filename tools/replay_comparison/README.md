# TLS Replay Comparison Receipt v0.1

This bounded, offline CodeYourCompliance artifact runs the **existing TLS replay runner** and compares its output against an explicitly supplied synthetic recorded assessment. The recorded baseline is **unattested**. A `matched` receipt is not proof that an independently authentic historical assessment was reproduced.

## Purpose

An audit reviewer has an old `PASS` result. The package closure validator reports all local dependencies are available. The reviewer runs the same TLS assessment again and gets another `PASS`.

The two results alone do not establish replay. The evidence, context, schemas, policy bytes, implementation version, engine path, and compared decision fields must agree. A new `PASS` against a different policy must not be recorded as `matched`.

This tool checks these bindings for **one** `tls-replay-v0.1` reference package. It is not a generic replay verifier or independently authenticated receipt system.

## Windows usage

Run from the repository root, using a Python environment with the existing TLS runner's `jsonschema` dependency installed. The comparison wrapper itself uses Python standard library, but the replay runner requires `jsonschema>=4.24,<5`. Use an approved offline wheelhouse when Internet access is not allowed.

```powershell
$repo = 'C:\CodeYourCompliance\evidence-validation-pipeline'
Set-Location $repo
python -c "import jsonschema"
python .\tools\replay_comparison\compare_replay.py `
  --manifest .\examples\replayable-tls-control\closure-manifest.json `
  --recorded .\tools\replay_comparison\fixtures\synthetic-recorded-builtin.json `
  --engine builtin
Write-Host "Replay comparison exit: $LASTEXITCODE"
```

`--output` may be used to write a **new** receipt file outside the evidence package. Without it, the receipt is only printed to stdout. Existing receipt paths and paths inside the evidence package are rejected. No evidence file or recorded baseline is modified. The runner's intermediate assessment is written to a temporary directory and removed afterward.

Tests use temporary synthetic packages and a subprocess-compatible fake replay runner. They do not execute the official Rego policy or connect to a target:

```powershell
python -m unittest discover -s .\tools\replay_comparison\tests -p "test_*.py" -v
```

To run the existing TLS runner through the OPA path, use `--engine opa` **only with a separately captured OPA baseline**, with an installed OPA executable. The included baseline is for `builtin`. Comparing it to `opa` is an engine mismatch and returns `input_mismatch` **without executing OPA**.

## Receipt interpretation

| `comparison_status` | Meaning | Exit |
| --- | --- | --- |
| `matched` | Supplied baseline binds the same local artifacts, decision path, selected stable result fields; the runner executed | 0 |
| `input_mismatch` | Recorded artifact binding, selected engine, or actual runner provenance differs | 1 |
| `decision_mismatch` | Runner made a decision but compared fields differ from the supplied baseline | 1 |
| `blocked` | Baseline invalid, package closure failed, subprocess failed, decision did not execute, or comparison could not proceed | 2 |

Every receipt explicitly records `runner_invoked`, `decision_executed`, `policy_artifact_executed`, the recorded and replayed result, and machine-readable `reason_codes`/`mismatched_fields`.

The `historical_replay_verified` field is **always false** in v0.1. The baseline and manifest are untrusted inputs unless independently anchored outside this tool; their SHA256 values in the receipt are identification metadata, not authentication.

For `builtin`, `decision_executed=true` does **not** imply Rego execution; `policy_artifact_executed=false`. The `opa` path, when separately configured, must show `policy_artifact_executed=true` to match an OPA baseline.

## Assumptions and exclusions

- Run this only against a **trusted local checkout**. The comparator executes the Python `replay.py` referenced by the package manifest. An attacker who can rewrite files, manifest, and baseline can make a new self-consistent but malicious package. The program does not sandbox or authenticate the executed code.
- The manifest and baseline hashes are local references, not a signed chain of custody.
- Runtime equivalence is `not_assessed`: Python, OPA, OS, wheel content, and engine build equivalence are not proven. The tool compares replay implementation name/version but does not certify its correctness.
- A successful local comparison is not control certification, audit acceptance, or a production compliance claim. Any decision mismatch indicates a comparison failure; it is not automatically target drift.
- The preflight checks closure before running, then checks again after execution. This is not atomic immutable storage, so a concurrent mutation cannot be ruled out.
- Evidence collection and remediation are not performed.

See [Replay Comparison Receipt Contract](../../docs/replay-comparison-receipt-contract.md), the existing [TLS Replay Package](../../examples/replayable-tls-control/README.md), and the [Closure Contract](../../docs/evidence-package-closure-contract.md).

## Origin and scope

**CodeYourCompliance** — https://www.codeyourcompliance.com

Original technical artifacts: https://github.com/codeyourcompliance/evidence-validation-pipeline

Attribution is requested for forks, references, adaptations, and discussions.

MAS TRM-inspired means engineering interpretation, not legal, regulatory, audit, or certification advice.
