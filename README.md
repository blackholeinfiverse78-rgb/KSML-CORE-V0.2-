# KSML Core v0.1 — Production Ready

**Kernel System Markup Language** - Deterministic, strict validation for system operations.

> **Status**: v0.1.0 (Locked & Production Ready)  
> **Philosophy**: Zero Silent Failures. Strict Validation. Deterministic Results.

---

## 🚀 Quick Start

### 1. Start the Validator Service
```bash
cd validator_service
python run_ui.py
```

### 2. Open Web UI
Browser: **http://localhost:8002**
- Live KSML validation
- Random sample data
- Clear error reporting

### 3. API Usage
```bash
curl -X POST http://localhost:8002/validate \
  -H "Content-Type: application/json" \
  -d @examples/valid_minimal.ksml.json
```

---

## 📝 Writing KSML

### Basic Structure
```json
{
  "ksml_version": "0.1.0",
  "metadata": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "author": "Your Name",
    "title": "Operation Name",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "configurations": {},
  "steps": [
    {
      "name": "Step Name",
      "action": "action_name",
      "parameters": {}
    }
  ]
}
```

### Rules
- **Version Required**: Must specify `"ksml_version": "0.1.0"`
- **No Unknown Fields**: Additional properties forbidden
- **Strict Types**: String ≠ Number ≠ Boolean
- **Required Fields**: All mandatory fields must be present

---

## 🛠 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web UI (redirects to `/static/index.html`) |
| `/validate` | POST | Validate KSML document |
| `/schema` | GET | Get canonical JSON schema |
| `/health` | GET | Service health check |

---

## 🚨 Error Codes

| Code | Description | Example |
|------|-------------|----------|
| **KSML_101** | Required field missing | Missing `action` in step |
| **KSML_102** | Type mismatch | `"123"` instead of `123` |
| **KSML_103** | Unknown field | Extra field not in schema |
| **KSML_003** | Version mismatch | Wrong `ksml_version` |

---

## 📁 Project Structure

```
ksml-core-v0.1/
├── schema/ksml_schema_v0.1.json    # Canonical schema
├── validator_service/              # FastAPI service + Web UI
├── examples/                       # Valid/invalid examples
├── docs/                          # Specifications
├── linting/                       # Error codes & rules
└── contract_tests/                # Test suite
```

---

## ✅ Testing

```bash
# Run all contract tests
cd contract_tests
python -m pytest test_contract.py -v

# Test with examples
python -c "from main import app; print('Service OK')"
```

---

## 🔒 Production Guarantees

- **Deterministic**: Same input = same output
- **Strict Validation**: No silent failures
- **Version Safe**: Immutable schema versions
- **Zero Dependencies**: Self-contained validation
- **Stateless**: Safe for containerization

---

## 📚 Documentation

- **Schema**: `schema/ksml_schema_v0.1.json`
- **Error Codes**: `linting/error_codes.md`
- **Design Principles**: `docs/design_principles.md`
- **Versioning Rules**: `docs/versioning_rules.md`
- **Examples**: `examples/README.md`
