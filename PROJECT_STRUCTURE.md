# KSML v0.2 Repository Structure

```
KSML-V1-Task-1-/
│
├── schema/                          # JSON Schemas
│   ├── ksml_schema_v0.1.json       # v0.1 schema (frozen)
│   └── ksml_schema_v0.2.json       # v0.2 schema (current)
│
├── validator_service/               # Validation Service
│   ├── static/                      # Web UI assets
│   ├── main.py                      # FastAPI validator service
│   ├── requirements.txt             # Python dependencies
│   ├── run_ui.py                    # Service launcher
│   └── test_ui.py                   # UI tests
│
├── linting/                         # Error Codes & Rules
│   ├── lint_rules.py                # Error code definitions
│   └── error_codes.md               # Error code documentation
│
├── contract_tests/                  # Test Suite
│   ├── test_contract.py             # v0.1 compatibility tests
│   ├── test_contract_v02.py         # v0.2 feature tests
│   ├── test_failure_modes.py        # Failure mode tests
│   ├── test_runner.py               # Test runner
│   └── repro_failure.py             # Failure reproduction
│
├── examples/                        # Example Documents
│   ├── valid_*.ksml.json            # Valid examples
│   ├── invalid_*.ksml.json          # Invalid examples
│   └── README.md                    # Examples guide
│
├── docs/                            # Documentation
│   ├── v0.2_scope.md                # v0.2 scope definition
│   ├── versioning_rules_v0.2.md     # Version compatibility rules
│   ├── safety_rules.md              # Consumer safety rules
│   ├── versioning_rules.md          # v0.1 versioning (legacy)
│   ├── design_principles.md         # Design philosophy
│   ├── ksml_scope.md                # KSML scope
│   ├── public_contracts.md          # Public API contracts
│   └── handover_notes.md            # Handover documentation
│
├── tools/                           # Utility Scripts
│   ├── verify_timeline.py           # Timeline verification
│   └── validate_v02_upgrade.py      # Upgrade validation
│
├── reports/                         # Verification Reports
│   ├── VERIFICATION_REPORT.md       # Detailed verification
│   └── VERIFICATION_SUMMARY.md      # Quick summary
│
├── README.md                        # Main documentation
├── QUICKSTART.md                    # Quick start guide
├── UPGRADE_GUIDE.md                 # Upgrade instructions
├── MIGRATION_NOTES.md               # Migration details
├── LOCK_v0.2                        # v0.2 release lock
├── LOCK                             # v0.1 release lock (legacy)
├── .gitignore                       # Git ignore rules
├── BUG_REPORT.md                    # Bug reporting template
├── TEST_RESULTS.md                  # Test results
├── UPGRADE_COMPLETE.md              # Upgrade completion notes
└── test_output.txt                  # Test output log
```

## Directory Purposes

### Core Directories
- **schema/**: JSON Schema definitions for all KSML versions
- **validator_service/**: FastAPI-based validation service with web UI
- **linting/**: Error codes, rules, and validation logic
- **contract_tests/**: Comprehensive test suite ensuring stability
- **examples/**: Reference documents for valid and invalid KSML

### Documentation
- **docs/**: Technical specifications and design documents
- **reports/**: Verification and validation reports

### Utilities
- **tools/**: Scripts for verification, validation, and maintenance

### Root Files
- **README.md**: Primary documentation and quick start
- **UPGRADE_GUIDE.md**: Step-by-step upgrade instructions
- **MIGRATION_NOTES.md**: Technical migration details
- **LOCK_v0.2**: Production release lock document

## File Naming Conventions

### Examples
- `valid_*.ksml.json` - Valid KSML documents
- `invalid_*.ksml.json` - Invalid KSML documents (for testing)

### Tests
- `test_*.py` - Test modules
- `test_contract*.py` - Contract tests
- `test_failure*.py` - Failure mode tests

### Documentation
- `*.md` - Markdown documentation
- `*_v0.2.md` - v0.2 specific documentation
- `*_rules.md` - Rule specifications

## Clean Repository Checklist

- [x] Schemas organized in schema/
- [x] Validator service in validator_service/
- [x] Tests in contract_tests/
- [x] Examples in examples/
- [x] Documentation in docs/
- [x] Utility scripts identified
- [x] Reports separated
- [x] Clear naming conventions
- [x] Logical directory structure