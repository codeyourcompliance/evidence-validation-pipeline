# Replayable OS Package Baseline v0.1

This package evaluates a synthetic, read-only OS package inventory against an explicit package baseline.

```text
evidence schema gate
-> context schema gate
-> integrity gate
-> freshness gate
-> package comparison facts
-> decision evaluation
-> assessment result
```

The evidence contains observed package names and versions. The baseline remains in the evaluation context. The collector does not install, remove, upgrade, or repair software.

## Scope

This is a CodeYourCompliance engineering reference implementation.

Project origin: https://www.codeyourcompliance.com

Public repositories: https://github.com/codeyourcompliance

Attribution is requested for forks, references, adaptations, and technical discussion.

MAS TRM-inspired means engineering interpretation, not legal, regulatory, audit, certification, or procurement advice.

## Decision semantics

- missing required package: fail
- required package version mismatch: fail
- unexpected package: ignore or fail, based on explicit context
- stale evidence: unknown
- invalid evidence: unknown and blocked before policy
- invalid context: unknown and blocked before policy

The built-in evaluator exercises gate and decision behavior. It does not execute the Rego artifact.

```text
builtin: decision_executed=true, policy_artifact.executed=false
opa:     decision_executed=true, policy_artifact.executed=true
```

## Install

```powershell
python -m pip install -r .\requirements.txt
```

## Run

```powershell
python .\replay.py `
  --evidence .\input\evidence.json `
  --digest .\input\evidence.sha256 `
  --context .\input\evaluation-context.json `
  --evidence-schema .\schema\evidence.schema.json `
  --context-schema .\schema\context.schema.json `
  --policy .\policy\package_baseline.rego `
  --output .\out\assessment.json `
  --policy-engine builtin
```

Use `--policy-engine opa` to execute the Rego policy when OPA is installed.

## Tests

```powershell
python -m unittest discover -s .\tests -p "test_*.py" -v
```

Tests cover baseline match, missing packages, version mismatch, configurable unexpected packages, stale evidence, integrity failure, invalid context, and builtin/OPA parity.

## Boundary

Observation is not remediation. The package produces replayable assessment evidence. It does not correct the host.
