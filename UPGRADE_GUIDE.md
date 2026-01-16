# KSML v0.2 Upgrade Guide

This guide describes how to upgrade existing KSML v0.1 documents to KSML v0.2.

## Fast Track Upgrade
Most v0.1 documents are already valid v0.2 documents structure-wise, **BUT** to fully adopt v0.2, you should:

1.  **Update Version Tag**: Change `ksml_version` from `"0.1.0"` to `"0.2.0"`.
2.  **Validate**: Run against the v0.2 validator.

```json
{
  "ksml_version": "0.2.0",  <-- CHANGED
  "metadata": { ... },
  ...
}
```

## detailed Changes

### 1. Consumer Safety Limits (Enforced)
In v0.2, the validator enforces strict limits. Ensure your documents comply:
*   **Max Document Size**: 1MB
*   **Max Steps**: 100
*   **Max Recursion Depth**: 10
*   **Max Dependencies**: 50

If your v0.1 document exceeds these, it was technically "unsafe" before. You must split it or optimize it.

### 2. Extensions
If you were stuffing metadata into undocumented fields (which was invalid in v0.1), you can now legally put them in `extensions`.
**Condition**: Keys must start with `x-`.

**Before (Invalid v0.1):**
```json
{
  "metadata": { "custom_field": "val" }  <-- FAIL (Additional Property)
}
```

**After (Valid v0.2):**
```json
{
  "extensions": {
    "x-custom-field": "val"
  }
}
```

### 3. Step Enhancements
You can now add `timeout_override`, `retry_policy`, and `conditions` to steps.
These are optional.

### 4. Metadata Enhancements
Add `version`, `environment`, and `dependencies` to `metadata` for better governance.

## Validator Upgrade
If you run the Validator Service:
*   Deploy the new `validator_service/` code.
*   It automatically accepts both `0.1.0` and `0.2.0`.
*   No configuration change needed.

## Compatibility Guarantee
*   **v0.1 documents** will continue to pass validation with `ksml_version: "0.1.0"`.
*   You are **NOT** forced to upgrade `ksml_version` if you don't need new features.