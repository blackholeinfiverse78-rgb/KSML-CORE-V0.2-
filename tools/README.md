# KSML Utility Tools

This directory contains utility scripts for KSML validation and verification.

## Scripts

### verify_timeline.py
**Purpose**: Verify all 15-day timeline deliverables are complete

**Usage**:
```bash
python verify_timeline.py
```

**Output**: Verification report showing completion status of all timeline requirements

---

### validate_v02_upgrade.py
**Purpose**: Comprehensive validation suite for v0.2 upgrade

**Usage**:
```bash
python validate_v02_upgrade.py
```

**Output**: Complete validation results including:
- File existence checks
- Schema validation
- Contract test execution
- Service health verification

---

## Requirements

All scripts require Python 3.7+ and dependencies from `validator_service/requirements.txt`

## Running All Validations

```bash
# Verify timeline deliverables
python verify_timeline.py

# Validate upgrade completion
python validate_v02_upgrade.py

# Run contract tests
cd ../contract_tests && python -m pytest -v
```