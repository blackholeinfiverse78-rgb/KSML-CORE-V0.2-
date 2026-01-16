# KSML Versioning Rules v0.2

**Authority**: This document defines the laws of version compatibility for KSML v0.2.

## 1. Version Compatibility Matrix

### v0.2 Validator Behavior
```
Input Version    | v0.2 Validator Action | Reason
-----------------|----------------------|------------------
0.1.0           | ✅ ACCEPT            | Full backward compatibility
0.2.0           | ✅ ACCEPT            | Native version
0.3.0           | ❌ REJECT            | Future minor version
1.0.0           | ❌ REJECT            | Different major version
invalid         | ❌ REJECT            | Malformed version
missing         | ❌ REJECT            | Required field
```

### Version Validation Logic
```python
def validate_version(ksml_version: str) -> tuple[bool, str]:
    """
    MUST accept: 0.1.0, 0.2.0
    MUST reject: everything else with clear reason
    """
    if not ksml_version:
        return False, "Missing required field 'ksml_version'"
    
    if ksml_version == "0.1.0":
        return True, "v0.1 compatibility mode"
    
    if ksml_version == "0.2.0":
        return True, "v0.2 native mode"
    
    # Parse and provide specific rejection reason
    try:
        major, minor, patch = ksml_version.split('.')
        major, minor, patch = int(major), int(minor), int(patch)
        
        if major != 0:
            return False, f"Unsupported major version {major}. Expected 0.x.x"
        
        if minor > 2:
            return False, f"Future version {ksml_version}. Maximum supported: 0.2.x"
        
        return False, f"Unsupported version {ksml_version}. Supported: 0.1.0, 0.2.0"
        
    except ValueError:
        return False, f"Invalid version format '{ksml_version}'. Expected semantic version (x.y.z)"
```

## 2. Schema Selection Logic

### Dual Schema Support
- **v0.1 documents**: Validated against v0.1 schema rules
- **v0.2 documents**: Validated against v0.2 schema with all features
- **No silent upgrades**: Version determines exact validation behavior

### Schema Loading Strategy
```python
def get_schema_for_version(version: str) -> dict:
    """Load appropriate schema based on document version"""
    if version == "0.1.0":
        return load_schema("ksml_schema_v0.1.json")
    elif version == "0.2.0":
        return load_schema("ksml_schema_v0.2.json")
    else:
        raise UnsupportedVersionError(f"No schema for version {version}")
```

## 3. Backward Compatibility Guarantees

### v0.1 Document Processing
- **Identical Validation**: v0.1 docs validate exactly as in v0.1 validator
- **Same Error Codes**: KSML_001, KSML_002, KSML_003, KSML_100-103 unchanged
- **Same Error Messages**: Exact message templates preserved
- **Same Performance**: No degradation in validation speed

### v0.2 Feature Isolation
- **Optional Only**: All v0.2 features are optional additions
- **No Interference**: v0.2 features don't affect v0.1 validation paths
- **Clear Boundaries**: v0.1 and v0.2 validation are separate code paths

## 4. Error Handling Evolution

### New Error Codes for v0.2
```python
KSML_V2_RULES = {
    # v0.2 specific errors
    "KSML_004": (Severity.ERROR, "Safety limit exceeded: {details}"),
    "KSML_005": (Severity.ERROR, "Invalid extension configuration: {details}"),
    "KSML_006": (Severity.ERROR, "Malformed dependency specification: {details}"),
    "KSML_007": (Severity.WARNING, "Deprecated v0.2 feature used: {details}"),
}
```

### Version-Specific Error Context
- **v0.1 errors**: No mention of v0.2 features in error messages
- **v0.2 errors**: Clear indication when v0.2-specific validation fails
- **Version hints**: Suggest version upgrade only when beneficial

## 5. Migration Path Clarity

### Upgrade Decision Matrix
```
Current State     | Recommended Action | Reason
------------------|-------------------|------------------
v0.1 working      | Stay on v0.1      | No breaking changes needed
Need new features | Upgrade to v0.2   | Access optional capabilities
Future planning   | Plan for v0.2     | Prepare for ecosystem evolution
```

### Safe Upgrade Process
1. **Test Current**: Ensure v0.1 documents validate in v0.2
2. **Add Features**: Incrementally add v0.2 optional features
3. **Update Version**: Change `ksml_version` to `0.2.0` when ready
4. **Validate**: Confirm all features work as expected

## 6. Consumer Safety Rules

### Version Announcement
- **Clear Declaration**: Every document MUST declare its target version
- **No Guessing**: Validator never assumes or infers version
- **Explicit Rejection**: Unknown versions fail with clear explanation

### Deterministic Behavior
- **Same Input = Same Output**: Guaranteed across version boundaries
- **No Silent Fallbacks**: Never downgrade features silently
- **Predictable Errors**: Same error for same invalid input

### Forward Compatibility Planning
- **Version Parsing**: Ready for future versions (0.3.0, 1.0.0)
- **Graceful Rejection**: Clear messages for unsupported versions
- **Upgrade Guidance**: Helpful suggestions for version mismatches

---

**IMPLEMENTATION REQUIREMENT**: All validators MUST implement this exact version handling logic to ensure ecosystem consistency.