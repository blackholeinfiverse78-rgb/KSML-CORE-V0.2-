# KSML Examples

**Quick Reference**: Copy these templates for your KSML documents.

## Valid Examples ✅

### `valid_minimal.ksml.json`
Smallest possible valid document:
```json
{
  "ksml_version": "0.1.0",
  "metadata": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "author": "Min",
    "title": "Minimal",
    "created_at": "2023-01-01T00:00:00Z"
  },
  "configurations": {},
  "steps": [{
    "name": "S1",
    "action": "noop",
    "parameters": {}
  }]
}
```

### `valid_complex.ksml.json`
Full-featured example with all optional fields.

## Invalid Examples ❌

### `invalid_missing_version.ksml.json`
- **Error**: KSML_101 - Missing `ksml_version`

### `invalid_type_mismatch.ksml.json`
- **Error**: KSML_102 - Wrong data types

### `invalid_example.ksml.json`
- **Error**: KSML_103 - Unknown field `unknown_field`

### `invalid_bad_action_format.ksml.json`
- **Error**: KSML_100 - Action pattern violation

## Usage

**Test with Web UI**: Load examples using buttons in http://localhost:8002

**Test with API**:
```bash
curl -X POST http://localhost:8002/validate \
  -H "Content-Type: application/json" \
  -d @valid_minimal.ksml.json
```
