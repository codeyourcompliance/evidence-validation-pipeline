package codeyourcompliance.tls_certificate

import rego.v1

default allow := false

allow if {
  input.derived_facts.days_to_expiry >= input.context.minimum_certificate_days_remaining
}

violations contains violation if {
  input.derived_facts.days_to_expiry < input.context.minimum_certificate_days_remaining
  violation := {
    "code": "TLS_CERTIFICATE_EXPIRY_THRESHOLD",
    "message": sprintf(
      "certificate has %d days remaining; minimum is %d",
      [input.derived_facts.days_to_expiry, input.context.minimum_certificate_days_remaining]
    )
  }
}
