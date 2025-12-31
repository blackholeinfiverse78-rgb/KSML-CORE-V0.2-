# KSML Public Contracts

**Status**: Stable (v0.1.0)  
**Authority**: This document binds the Validator Service.

## 1. Validation Endpoint

**URL**: `POST /validate`  
**Auth**: None (Public)

### Request
- **Content-Type**: `application/json`
- **Body**: A complete KSML Document.
- **Constraints**: Max size 10MB (suggested, not enforced by spec).

```json
{
  "ksml_version": "0.1.0",
  "metadata": { ... },
  "steps": [ ... ]
}
```

### Response
- **Content-Type**: `application/json`
- **Status Code**: `200 OK` (Even for validation failures)

**Success (Valid Document)**:
```json
{
  "valid": true,
  "ksml_version": "0.1.0",
  "errors": [],
  "warnings": []
}
```

**Success (Invalid Document)**:
```json
{
  "valid": false,
  "ksml_version": "0.1.0",
  "errors": [
    {
      "code": "KSML_101",
      "message": "Required field missing: action",
      "path": "steps.0",
      "severity": "ERROR"
    }
  ],
  "warnings": []
}
```

### Error Envelopes (Apps Level)
If the service itself fails (e.g., malformed JSON body), it returns standard HTTP error codes.

**400 Bad Request (Malformed JSON)**:
```json
{
  "detail": "JSON parse error..."
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Internal System Error: KSML_001"
}
```

## 2. Schema Endpoint

**URL**: `GET /schema`  
**Auth**: None

### Response
- **Content-Type**: `application/json`
- **Body**: The Canonical JSON Schema (Draft-07).

## 4. Root Endpoint

**URL**: `GET /`  
**Behavior**: Redirects to `/health`.

## 5. Health Endpoint

**URL**: `GET /health`  
**Auth**: None

### Response
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```
