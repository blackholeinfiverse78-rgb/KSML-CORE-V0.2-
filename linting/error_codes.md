# KSML Error Reference

**Quick Lookup**: Find your error code and fix it fast.

## System Errors

| Code | Description | Fix |
|------|-------------|-----|
| **KSML_001** | Internal System Error | Contact support |
| **KSML_002** | Missing Version | Add `"ksml_version": "0.1.0"` |
| **KSML_003** | Unsupported Version | Use `"ksml_version": "0.1.0"` only |

## Schema Violations

| Code | Description | Fix |
|------|-------------|-----|
| **KSML_100** | Generic Schema Violation | Check error message details |
| **KSML_101** | Required Field Missing | Add the missing field |
| **KSML_102** | Type Mismatch | Fix data type (string vs number) |
| **KSML_103** | Unknown Field | Remove the extra field |

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

## Testing Errors

Use the **Web UI** at http://localhost:8002:
1. Click "Load Invalid Example"
2. See the error in action
3. Fix it and validate again
