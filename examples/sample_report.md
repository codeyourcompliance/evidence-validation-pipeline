# Sample MAS TRM-Aligned Audit Narrative

## Evidence Summary

- Evidence ID: `sample-evidence-001`
- Host ID: `sample-host-001`
- Evidence type: `tls_certificate_lifecycle`
- Collection method: `read_only`
- Collector: `ansible-readonly`
- Collected at: `2026-04-28T09:30:00Z`
- Integrity status: `verified`

## Technical Finding

The HTTPS service was operating with a TLS certificate approaching expiry within the defined threshold.

The derived evidence facts indicate:

- Certificate days to expiry: `2`
- Expiring within 30 days: `true`
- Signature algorithm family: `sha256-rsa`
- Public key strength: `2048 bits`

## Audit Narrative

Based on cryptographically verified TLS certificate evidence collected on 28 April 2026, the HTTPS service was operating with a certificate approaching expiry within the defined threshold. This condition weakens assurance over the TLS certificate lifecycle and does not align with MAS TRM-inspired expectations for maintaining strong cryptographic controls and effective technology risk management.

## Evidence Integrity Statement

The audit narrative was generated only after evidence integrity verification completed successfully.

If the evidence hash does not match the expected value, this report should not be treated as a pass or fail result. The correct status should be `invalid_evidence`.

## Scope and Limitations

This sample report is a demonstration artifact.

It does not prove complete MAS TRM compliance. It does not provide legal, regulatory, audit, or certification advice. It does not replace auditors, risk owners, or formal regulatory interpretation.

The purpose of this report is to demonstrate how a technical finding can be traced back to timestamped, integrity-checked, machine-evaluable evidence.

## Pattern Demonstrated

Where technical evidence exists, compliance conclusions should be replayable.
