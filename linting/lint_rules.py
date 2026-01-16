# Strict Linting Rules

class Severity:
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"

# Rule Definitions
# Structure: Code -> (Severity, Message Template)
KSML_RULES = {
    # System / Versioning
    "KSML_001": (Severity.ERROR, "Internal System Error: {details}"),
    "KSML_002": (Severity.ERROR, "Missing required field 'ksml_version'."),
    "KSML_003": (Severity.ERROR, "Unsupported ksml_version '{version}'. Expected '0.1.0'."),
    
    # structural
    "KSML_100": (Severity.ERROR, "Schema Violation: {details}"),
    "KSML_101": (Severity.ERROR, "Required field missing: {field}"),
    "KSML_102": (Severity.ERROR, "Type Mismatch: Expected {expected}, got {actual}."),
    "KSML_103": (Severity.ERROR, "Unknown field '{field}' is not allowed (additionalProperties: false)."),
    
    # Deprecation (Reserved for future)
    "KSML_200": (Severity.WARNING, "Deprecated feature used: {details}"),
}

# v0.2 Additional Rules
KSML_V2_RULES = {
    # v0.2 Safety and Extensions
    "KSML_004": (Severity.ERROR, "Safety limit exceeded: {details}"),
    "KSML_005": (Severity.ERROR, "Invalid extension configuration: {details}"),
    "KSML_006": (Severity.ERROR, "Malformed dependency specification: {details}"),
    "KSML_007": (Severity.WARNING, "Deprecated v0.2 feature used: {details}"),
}

def get_rule(code):
    return KSML_RULES.get(code, (Severity.ERROR, "Unknown Error"))

def get_rule_v2(code):
    """Get rule from v0.2 rules or fall back to v0.1 rules"""
    return KSML_V2_RULES.get(code, get_rule(code))
