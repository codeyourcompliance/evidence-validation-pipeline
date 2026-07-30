package codeyourcompliance.os_package_baseline

import rego.v1

default allow := false

allow if {
  count(input.derived_facts.missing_packages) == 0
  count(input.derived_facts.version_mismatches) == 0
  not unexpected_packages_block
}

unexpected_packages_block if {
  input.context.unexpected_package_mode == "fail"
  count(input.derived_facts.unexpected_packages) > 0
}

violations contains violation if {
  pkg := input.derived_facts.missing_packages[_]
  violation := {"code": "MISSING_REQUIRED_PACKAGE", "message": sprintf("required package missing: %s", [pkg.name])}
}

violations contains violation if {
  mismatch := input.derived_facts.version_mismatches[_]
  violation := {"code": "PACKAGE_VERSION_MISMATCH", "message": sprintf("package %s is %s; required %s", [mismatch.name, mismatch.observed_version, mismatch.required_version])}
}

violations contains violation if {
  input.context.unexpected_package_mode == "fail"
  pkg := input.derived_facts.unexpected_packages[_]
  violation := {"code": "UNEXPECTED_PACKAGE", "message": sprintf("unexpected package observed: %s %s", [pkg.name, pkg.version])}
}
