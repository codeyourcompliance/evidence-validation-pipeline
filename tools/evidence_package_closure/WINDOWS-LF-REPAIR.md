# Windows: repairing a checked-out TLS fixture without rewriting the manifest

This is a **local development worktree repair**. It is not an evidence collector, policy evaluation, or remediation against an observed production control. The closure validator itself stays read-only.

## Observed failure

On 2026-11-01, a Windows clone of `codeyourcompliance/evidence-validation-pipeline` reported all eight TLS files as:

```text
i/lf    w/crlf    attr/text eol=lf
```

Their SHA256 values differed from the manifest. A fresh synthetic unit suite passed, but the checked-in fixture regression test correctly failed.

On this host, both `git restore --worktree` and `git -c core.autocrlf=false checkout-index --force` returned exit code 0 without changing the eight working-tree files to LF. These commands must **not** be treated as sufficient without checking the actual bytes.

The successful repair compared the bytes stored in the Git index with the bytes in each local file and only wrote the original index bytes after verifying that every difference was CRLF versus LF. Eight files were repaired. Subsequent results were:

- `git ls-files --eol`: eight `i/lf w/lf attr/text eol=lf` entries.
- TLS closure validator: eight `sha256_match` entries, `closure_status=satisfied`, exit 0.
- Standard-library tests: 21/21 passing, exit 0.
- Independent raw-blob comparison (`git rev-parse :path` vs `git hash-object --no-filters path`): eight byte-identical results.

Git `status` still reported eight modified files immediately after the successful byte repair, despite `git diff --name-status` producing no changes. Do not stage or reset these files merely to clear the status. Refresh index stat metadata separately and investigate if the status persists.

## Safety boundary

Only use this against a **trusted local clone** whose checked-in manifest and eight Git index blobs are the intended reference. The repair is conditional:

1. The index manifest declares exactly the eight fixed TLS paths.
2. The local manifest parses to the same object as the index manifest.
3. The SHA256 of each index blob matches its manifest entry.
4. Every existing worktree file is already equal to the index blob, or becomes equal when CRLF is converted to LF.
5. All eight paths pass preflight before any writes.

The script does not regenerate SHA256 values, change the manifest or Git index, run replay, or touch unrelated files. Files can still change concurrently between checks; this is a local maintenance action, not an atomic evidence-custody operation.

## Procedure: PowerShell with Python standard library

Run from PowerShell. This creates a temporary Python script outside the repository and deletes it afterward.

```powershell
$repo = "C:\CodeYourCompliance\evidence-validation-pipeline"

$repair = @'
import hashlib
import json
import subprocess
import sys
from pathlib import Path

repo = Path(sys.argv[1]).resolve()
base = "examples/replayable-tls-control"

paths = (
    "input/evidence.json",
    "input/evidence.sha256",
    "schema/evidence.schema.json",
    "input/evaluation-context.json",
    "schema/context.schema.json",
    "policy/tls_certificate.rego",
    "replay.py",
    "requirements.txt",
)

def index_bytes(path):
    return subprocess.check_output(
        ["git", "-C", str(repo), "show", ":" + path]
    )

manifest = json.loads(
    index_bytes(base + "/closure-manifest.json")
)
entries = manifest.get("artifacts", [])
by_path = {entry["path"]: entry for entry in entries}

if (
    manifest.get("profile") != "tls-replay-v0.1"
    or len(entries) != 8
    or len(by_path) != 8
    or set(by_path) != set(paths)
):
    raise SystemExit("BLOCKED: Unexpected manifest structure")

local_manifest = json.loads(
    (repo / base / "closure-manifest.json").read_bytes()
)
if local_manifest != manifest:
    raise SystemExit("BLOCKED: Manifest differs from Git index")

pending = []

# All eight files are checked before any modifications.
for rel in paths:
    target = repo / base / rel
    if target.is_symlink() or not target.is_file():
        raise SystemExit("BLOCKED: Missing file or symlink: " + rel)

    original = target.read_bytes()
    canonical = index_bytes(base + "/" + rel)
    expected = by_path[rel]["sha256"]

    if hashlib.sha256(canonical).hexdigest() != expected:
        raise SystemExit("BLOCKED: Index SHA256 mismatch: " + rel)

    if original == canonical:
        print("ALREADY LF:", rel)
    elif original.replace(b"\r\n", b"\n") == canonical:
        pending.append((target, original, canonical))
        print("CRLF ONLY:", rel)
    else:
        raise SystemExit("BLOCKED: Unexpected content difference: " + rel)

for target, original, canonical in pending:
    if target.read_bytes() != original:
        raise SystemExit("BLOCKED: File changed during repair")
    target.write_bytes(canonical)
    if target.read_bytes() != canonical:
        raise SystemExit("BLOCKED: Write verification failed")
    print("REPAIRED:", target.relative_to(repo))

print("BYTE CHECK PASSED: 8 files")
print("REPAIRED COUNT:", len(pending))
'@

$tempScript = Join-Path $env:TEMP (
    "cyc-lf-repair-" + [guid]::NewGuid().ToString("N") + ".py"
)
[System.IO.File]::WriteAllText(
    $tempScript, $repair,
    (New-Object System.Text.UTF8Encoding($false))
)

try {
    python $tempScript $repo
    if ($LASTEXITCODE -ne 0) {
        throw "Byte repair blocked or failed"
    }
}
finally {
    Remove-Item -LiteralPath $tempScript -Force -ErrorAction SilentlyContinue
}
```

## Inspect the result

Use the exact eight paths from the manifest and inspect `git ls-files --eol -- <paths>`. All eight should show `i/lf w/lf attr/text eol=lf`. Re-run the closure validator and all 21 tests using the commands in [README](README.md).

If Git reports tracked modifications while `git diff --name-status` is empty and raw worktree blobs are identical to the index blobs, try the **index metadata refresh**:

```powershell
git -C $repo update-index --refresh
git -C $repo status --short --branch
```

`update-index --refresh` updates cached file stat information; it does not replace file contents or change the blob identities. If `M` persists, stop and investigate the index/filter status. Do **not** use `git add` or `git reset --hard` just to silence it.

## Origin and scope

This document originates from **CodeYourCompliance**.

- https://www.codeyourcompliance.com
- https://github.com/codeyourcompliance
- https://github.com/codeyourcompliance/evidence-validation-pipeline

Attribution is requested for forks, references, adaptations, and discussions.

MAS TRM-inspired means engineering interpretation, not legal, regulatory, audit, or certification advice.
