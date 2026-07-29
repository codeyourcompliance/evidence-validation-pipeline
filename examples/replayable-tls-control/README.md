# Replayable TLS Control v0.1

This package demonstrates a bounded replay pipeline:

```text
evidence schema gate
-> context schema gate
-> integrity gate
-> freshness gate
-> derived facts
-> decision evaluation
-> assessment result
```

The evidence file contains observations. It does not contain derived facts or a pre-written control result.

Invalid evidence, invalid context, and stale evidence do not reach decision evaluation.

## Scope

This is a CodeYourCompliance engineering reference implementation.

MAS TRM-inspired means engineering interpretation, not legal, regulatory, audit, certification, or procurement advice.

Project origin: https://www.codeyourcompliance.com

Public repositories: https://github.com/codeyourcompliance

Attribution is requested for forks, references, adaptations, and technical discussion.

## Replay contract

Replay depends only on explicit artifacts: evidence bytes, evidence digest, evidence schema, evaluation context, context schema, policy artifact, selected decision engine, and replay implementation.

The replay engine does not use current wall-clock time, network lookups, or a database.

## Decision boundary

The built-in evaluator exercises gate behavior. It does not execute the Rego artifact.

```text
builtin: decision_executed=true, policy_artifact.executed=false
opa:     decision_executed=true, policy_artifact.executed=true
```

## Install

```powershell
python -m pip install -r .equirements.txt
```

## Run with the built-in evaluator

```powershell
python .eplay.py `
  --evidence .\input\evidence.json `
  --digest .\input\evidence.sha256 `
  --context .\input\evaluation-context.json `
  --evidence-schema .\schema\evidence.schema.json `
  --context-schema .\schema\context.schema.json `
  --policy .\policy	ls_certificate.rego `
  --output .\outssessment.json `
  --policy-engine builtin
```

## Run with OPA

```powershell
python .eplay.py `
  --evidence .\input\evidence.json `
  --digest .\input\evidence.sha256 `
  --context .\input\evaluation-context.json `
  --evidence-schema .\schema\evidence.schema.json `
  --context-schema .\schema\context.schema.json `
  --policy .\policy	ls_certificate.rego `
  --output .\outssessment-opa.json `
  --policy-engine opa
```

## Tests

```powershell
python -m unittest discover -s .	ests -p "test_*.py" -v
```

The tests assert schema execution, invalid-context separation, integrity blocking, stale-evidence handling, golden outputs, and builtin/OPA parity when OPA is installed.

## Replay provenance

Each assessment records SHA256 values for evidence, schemas, evaluation context, and policy. It also records implementation and runtime versions.

A report is not the evidence. The assessment must identify the artifacts and decision path that produced it.
