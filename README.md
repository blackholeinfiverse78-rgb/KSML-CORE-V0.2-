# KSML Core v0.2 — Production Ready

**Kernel System Markup Language** - Deterministic, strict validation for system operations with enhanced capabilities.

> **Status**: v0.2.0 (Production Ready)  
> **Philosophy**: Zero Silent Failures. Strict Validation. Deterministic Results. Consumer Safety.

---

## Quick Links

- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Testing](#testing)
- [Upgrade Guide](UPGRADE_GUIDE.md)
- [Migration Notes](MIGRATION_NOTES.md)

---

## Quick Start

### 1. Start the Validator Service
```bash
cd validator_service
python run_ui.py
```

### 2. Open Web UI
Browser: **http://localhost:8002**

### 3. API Usage
```bash
# Validate v0.1 document
curl -X POST http://localhost:8002/validate \
  -H "Content-Type: application/json" \
  -d @examples/valid_minimal.ksml.json

# Validate v0.2 document
curl -X POST http://localhost:8002/validate \
  -H "Content-Type: application/json" \
  -d @examples/valid_v02_showcase.ksml.json
```

---

## Project Structure

```
KSML-V1-Task-1-/
├── schema/              # JSON Schemas (v0.1 & v0.2)
├── validator_service/   # FastAPI validation service
├── linting/             # Error codes & rules
├── contract_tests/      # Comprehensive test suite
├── examples/            # Valid & invalid examples
├── docs/                # Technical documentation
├── tools/               # Utility scripts
└── reports/             # Verification reports
```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed structure.

---

## Version Compatibility

| Validator | Accepts v0.1 | Accepts v0.2 | Breaking Changes |
|-----------|--------------|--------------|------------------|
| v0.2      | ✓ Yes        | ✓ Yes        | None             |

**Backward Compatible**: All v0.1 documents work unchanged in v0.2 validator.

---

## What's New in v0.2

### Enhanced Metadata
- Document versioning
- Environment targeting (dev/staging/prod)
- Dependency tracking

### Step Enhancements
- Per-step timeout overrides
- Retry policy configuration
- Conditional execution metadata

### Consumer Safety
- Document size limits (1MB)
- Step count limits (100 max)
- Malformed structure detection
- Resource exhaustion prevention

### Extensions Framework
- Vendor-specific extensions (x- prefix)
- Future-proof extensibility

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web UI |
| `/validate` | POST | Validate KSML document (v0.1 or v0.2) |
| `/schema` | GET | Get v0.2 schema |
| `/schema/v0.1` | GET | Get v0.1 schema |
| `/schema/v0.2` | GET | Get v0.2 schema |
| `/health` | GET | Service health check |

---

## Error Codes

### v0.1 Error Codes (Preserved)
| Code | Description |
|------|-------------|
| KSML_001 | Internal System Error |
| KSML_002 | Missing ksml_version |
| KSML_003 | Unsupported version |
| KSML_100 | Schema Violation |
| KSML_101 | Required field missing |
| KSML_102 | Type mismatch |
| KSML_103 | Unknown field |

### v0.2 New Error Codes
| Code | Description |
|------|-------------|
| KSML_004 | Safety limit exceeded |
| KSML_005 | Invalid extension config |
| KSML_006 | Malformed dependency |

See [linting/error_codes.md](linting/error_codes.md) for details.

---

## Testing

```bash
# Run all tests
cd contract_tests
python -m pytest -v

# Run specific test suites
python -m pytest test_contract.py -v          # v0.1 compatibility
python -m pytest test_contract_v02.py -v      # v0.2 features
python -m pytest test_failure_modes.py -v     # Failure modes

# Verify timeline deliverables
cd ../tools
python verify_timeline.py

# Validate upgrade
python validate_v02_upgrade.py
```

**Test Results**: 48/48 tests passing (100%)

---

## Documentation

### Core Documentation
- [README.md](README.md) - This file
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Repository structure

### Upgrade Documentation
- [UPGRADE_GUIDE.md](UPGRADE_GUIDE.md) - Step-by-step upgrade instructions
- [MIGRATION_NOTES.md](MIGRATION_NOTES.md) - Technical migration details

### Technical Specifications
- [docs/v0.2_scope.md](docs/v0.2_scope.md) - v0.2 scope definition
- [docs/versioning_rules_v0.2.md](docs/versioning_rules_v0.2.md) - Version compatibility
- [docs/safety_rules.md](docs/safety_rules.md) - Consumer safety rules
- [docs/design_principles.md](docs/design_principles.md) - Design philosophy

### Verification Reports
- [reports/VERIFICATION_REPORT.md](reports/VERIFICATION_REPORT.md) - Detailed verification
- [reports/VERIFICATION_SUMMARY.md](reports/VERIFICATION_SUMMARY.md) - Quick summary

---

## Production Guarantees

### v0.1 Compatibility
- ✓ Identical validation for v0.1 documents
- ✓ Same error codes and messages
- ✓ Same performance characteristics
- ✓ Zero breaking changes

### v0.2 Enhancements
- ✓ Consumer safety protections
- ✓ Optional features only
- ✓ Deterministic behavior
- ✓ Strict validation maintained

### Universal Guarantees
- ✓ Zero silent failures
- ✓ Deterministic results
- ✓ Version safe
- ✓ Stateless operation
- ✓ Production ready

---

## Support

### Getting Help
- Check [examples/](examples/) for reference documents
- Review [linting/error_codes.md](linting/error_codes.md) for error explanations
- See [UPGRADE_GUIDE.md](UPGRADE_GUIDE.md) for migration help

### Reporting Issues
Use [BUG_REPORT.md](BUG_REPORT.md) template for bug reports

---

## License & Status

**Status**: LOCKED AND PRODUCTION READY  
**Version**: v0.2.0  
**Release**: See [LOCK_v0.2](LOCK_v0.2)

---

**KSML Core v0.2** - Precision engineering for deterministic system operations.