# Replayable TLS Control v0.1

This reference package demonstrates a bounded replay pipeline:

```text
schema gate
-> integrity gate
-> freshness gate
-> derived facts
-> policy evaluation
-> assessment result
```

The evidence file does not contain derived facts or a pre-written control result.
Invalid or stale evidence never reaches policy evaluation.

## Scope

This is a CodeYourCompliance engineering reference implementation.
MAS TRM-inspired means engineering interpretation, not legal, regulatory, audit, or certification advice.

Project origin: https://www.codeyourcompliance.com
Public repositories: https://github.com/codeyourcompliance

Attribution is requested for forks, references, adaptations, and technical discussion.

## Run with the built-in deterministic evaluator

From this directory:

```powershell
python .\replay.py `
  --evidence .\input\evidence.json `
  --digest .\input\evidence.sha256 `
  --context .\input\evaluation-context.json `
  --policy .\policy\tls_certificate.rego `
  --output .\out\assessment.json `
  --policy-engine builtin
```

The built-in evaluator exists so the gate behavior can be tested with the Python standard library only.

## Run with OPA

Install `opa`, place it on `PATH`, then run:

```powershell
python .\replay.py `
  --evidence .\input\evidence.json `
  --digest .\input\evidence.sha256 `
  --context .\input\evaluation-context.json `
  --policy .\policy\tls_certificate.rego `
  --output .\out\assessment-opa.json `
  --policy-engine opa
```

## Tests

```powershell
python -m unittest discover -s .\tests -p "test_*.py" -v
```

The tests prove four boundaries:

1. Valid fresh evidence can produce `pass`.
2. Valid fresh evidence can produce `fail`.
3. A payload changed after sealing becomes `invalid_evidence` and policy is not executed.
4. Stale evidence becomes `stale_evidence`; control status remains `unknown` and policy is not executed.

## Replay boundary

Deterministic replay requires fixed evidence bytes, digest, evaluation context, policy, and implementation version.
A report is not the evidence. The assessment must retain the gate trace that explains whether policy execution was admissible.
