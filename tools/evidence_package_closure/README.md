# Evidence Package Closure Validator v0.1

This is a **read-only, offline preflight** for the repository's existing synthetic TLS replay example.

It checks whether eight required files exist at the expected relative paths, match the SHA256 values declared in a local manifest, and include a consistent evidence digest reference.

It does not perform replay or evaluate a control.

## Run from the repository root on Windows PowerShell

Requirements: Python 3.10+ using **only the standard library**. No OPA, `jsonschema` installation, API credentials, remote target, or network access is needed for this check.

```powershell
python .\tools\evidence_package_closure\validate_closure.py --manifest .\examples\replayable-tls-control\closure-manifest.json
```

Exit code `0` means the local fixed-profile closure check is `satisfied`. Exit code `1` means `blocked`, with reasons in the emitted JSON.

PowerShell can also capture the result without modifying the evidence:

```powershell
python .\tools\evidence_package_closure\validate_closure.py --manifest .\examples\replayable-tls-control\closure-manifest.json > .\closure-check-result.json
$LASTEXITCODE
```

Do not put the output file into a source directory that is itself part of an independently managed evidence package.

## Windows line-ending repair after upgrading an existing clone

The TLS closure manifest pins the **exact LF bytes** stored in Git. Windows checkout configuration can leave existing files as CRLF (`i/lf w/crlf attr/text eol=lf`) even after the root `.gitattributes` specifies LF.

On a tested Windows clone, both `git restore --worktree` and `git checkout-index --force` returned exit code 0 but left the eight files as CRLF. Those commands are **not a verified repair on that host**. Repeatedly retrying them or rewriting the manifest SHA256 values is not appropriate.

The verified repair was a guarded, eight-file operation using the exact **Git index bytes**. Each index blob matched the manifest, and each local file differed only by CRLF before being rewritten to LF. The on-host result was eight `w/lf` files, closure exit 0, and 21/21 passing tests.

Follow [Windows TLS fixture byte repair](WINDOWS-LF-REPAIR.md) for the verified script, safety checks, and a separate Git index stat-cache refresh step. Repairing byte identity does not necessarily clear a stale Git `M` status immediately. Do not use `git add` or `git reset --hard` just to hide that status.

## Run tests

From repository root:

```powershell
python -m unittest discover -s .\tools\evidence_package_closure\tests -p "test_*.py" -v
```

Tests construct temporary synthetic packages. No source host, external service, or installed OPA runtime is used.

Test cases include missing roles, missing or modified files, digest-file mismatch, malformed SHA256 fields, duplicate JSON keys, unexpected file paths, attempted traversal, symlinks, and deterministic repeated reads.

## Profile and manifest

Manifest: [TLS Closure Manifest](../../examples/replayable-tls-control/closure-manifest.json).

The checker intentionally accepts one profile only: `tls-replay-v0.1`.

Required roles and paths are pinned in the Python validator. Each role must have an actual file and a matching SHA256 value. The separate `evidence.sha256` file must also match the evidence bytes.

Manifest references are relative to the directory containing the manifest. Path escaping and symlink traversal are rejected.

```text
role/path check
-> files present
-> SHA256 correspondence
-> evidence digest binding
-> closure_status = satisfied / blocked
```

**Not performed:** authenticated manifest verification, origin authentication, schema evaluation, dependency installation, policy evaluation, runtime equivalence testing, ZIP/TAR generation, or policy replay.

The manifest is a supplied reference. Anyone able to modify both the manifest and the files can generate an internally consistent package. This validator does not prevent that.

Results retain `replay_executed=false`, `decision_executed=false`, and `control_status=unknown` even when closure is satisfied.

## Documentation

See [Evidence Package Closure Contract](../../docs/evidence-package-closure-contract.md) and [Current Implementation Status](../../docs/current-implementation-status.md).

## Origin and Scope

This artifact originates from **CodeYourCompliance**.

- Website: https://www.codeyourcompliance.com/
- GitHub organization: https://github.com/codeyourcompliance
- Original repository: https://github.com/codeyourcompliance/evidence-validation-pipeline

Attribution is requested for forks, references, adaptations, and discussions.

MAS TRM-inspired means engineering interpretation, not legal, regulatory, audit, certification, procurement, implementation, or compliance advice.
