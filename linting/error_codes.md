# KSML Error Reference v0.2

**Quick Lookup**: Find your error code and fix it fast.

## System Errors

| Code | Description | Fix |
|------|-------------|-----|
| **KSML_001** | Internal System Error | Contact support |
| **KSML_002** | Missing Version | Add `"ksml_version": "0.1.0"` or `"0.2.0"` |
| **KSML_003** | Unsupported Version | Use `"ksml_version": "0.1.0"` or `"0.2.0"` |

## Schema Violations

| Code | Description | Fix |
|------|-------------|-----|
| **KSML_100** | Generic Schema Violation | Check error message details |
| **KSML_101** | Required Field Missing | Add the missing field |
| **KSML_102** | Type Mismatch | Fix data type (string vs number) |
| **KSML_103** | Unknown Field | Remove the extra field |

## v0.2 Safety & Extensions

| Code | Description | Fix |
|------|-------------|-----|
| **KSML_004** | Safety Limit Exceeded | Reduce document size or step count |
| **KSML_005** | Invalid Extension Config | Fix extensions block structure |
| **KSML_006** | Malformed Dependency | Fix dependency specification |
| **KSML_007** | Deprecated v0.2 Feature | Update to current syntax |

---

## Common Fixes

### Missing Action (KSML_101)
```json
// ❌ Wrong
{
  "name": "My Step",
  "parameters": {}
}

// ✅ Fixed
{
  "name": "My Step",
  "action": "my_action",
  "parameters": {}
}
```

### Type Mismatch (KSML_102)
```json
// ❌ Wrong
{
  "max_retries": "3"
}

// ✅ Fixed
{
  "max_retries": 3
}
```

### Unknown Field (KSML_103)
```json
// ❌ Wrong
{
  "name": "Step",
  "action": "test",
  "parameters": {},
  "my_custom_field": "value"
}

// ✅ Fixed
{
  "name": "Step",
  "action": "test",
  "parameters": {}
}
```

### Safety Limit Exceeded (KSML_004)
```json
// ❌ Wrong - Too many steps
{
  "ksml_version": "0.2.0",
  "steps": [ /* 150 steps */ ]
}

// ✅ Fixed - Within limit
{
  "ksml_version": "0.2.0",
  "steps": [ /* 50 steps */ ]
}
```

### Invalid Extension Config (KSML_005)
```json
// ❌ Wrong
{
  "ksml_version": "0.2.0",
  "extensions": "invalid"
}

// ✅ Fixed
{
  "ksml_version": "0.2.0",
  "extensions": {
    "capabilities": ["retry"]
  }
}
```

## Version-Specific Behavior

### v0.1 Documents
- Only codes KSML_001-003, KSML_100-103 possible
- Identical error messages to v0.1 validator
- No safety limit checks

### v0.2 Documents
- All error codes available
- Additional safety checks active
- Enhanced error context

## Testing Errors

Use the **Web UI** at http://localhost:8002:
1. Click "Load Invalid Example"
2. See the error in action
3. Fix it and validate again
