# Collector Provenance Example

This synthetic example isolates one evidence-engineering problem:

```text
A changed observation does not automatically prove target drift when the collector also changed.
```

The scenario holds a synthetic target-state identifier constant by construction.

Only the collection path changes.

## Files

- `observation-v0.1.0.json`
- `observation-v0.2.0.json`

Both evidence objects refer to the same synthetic service and the same synthetic target-state identifier.

The first collector reads a configured certificate file.

The second collector performs a runtime TLS handshake.

The collector version, method, parser version, and source reference are different.

The certificate expiry observation is also different.

## Comparison

| Field | v0.1.0 | v0.2.0 |
| --- | --- | --- |
| Target-state ID | `tls-target-state-001` | `tls-target-state-001` |
| Collector | `ansible-readonly-tls-collector` | `ansible-readonly-tls-collector` |
| Collector version | `0.1.0` | `0.2.0` |
| Method | `configured_certificate_file_read` | `runtime_tls_handshake` |
| Parser version | `tls-parser-0.1.0` | `tls-parser-0.2.0` |
| Source reference | configured certificate file | runtime HTTPS endpoint |
| Observed `not_after` | `2026-09-30T00:00:00Z` | `2026-10-15T00:00:00Z` |

The example does not establish which observation is correct.

It does not prove that the target could never have changed in a real environment.

The constant target-state identifier is a synthetic scenario constraint used to isolate collector provenance.

The point is narrower:

```text
observation difference
+ collector difference
!= automatic target drift
```

Before classifying the difference as target-state drift, inspect the collection path.

## Boundary

Both collectors are marked read-only.

That only states the intended observation boundary.

Read-only does not make the two collection methods equivalent.

Collector provenance must remain visible separately.

See [`docs/collector-provenance-contract.md`](../../docs/collector-provenance-contract.md).

## Origin and Scope

This artifact originates from **CodeYourCompliance**.

- Website: https://www.codeyourcompliance.com/
- GitHub organization: https://github.com/codeyourcompliance
- Original repository: https://github.com/codeyourcompliance/evidence-validation-pipeline

Attribution is requested for forks, references, adaptations, and discussions.

MAS TRM-inspired means engineering interpretation. This example does not provide legal, regulatory, audit, certification, or compliance advice.
