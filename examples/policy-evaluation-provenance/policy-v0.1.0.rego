package codeyourcompliance.policy_evaluation_provenance

import rego.v1

default allow := false

allow if {
  input.normalized_fact.days_to_expiry >= input.evaluation_context.minimum_certificate_days_remaining
}
