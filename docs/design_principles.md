# KSML Design Principles

## 1. Determinism
Validation is a pure function: `f(document) -> result`. 
- No network calls.
- No database lookups.
- No random seeds.
- No datetime dependencies.

## 2. Explicitness
- **No Magic**: Implicit behavior is forbidden.
- **Required Fields**: If a field is meaningful, it is required.
- **No Unknowns**: `additionalProperties: false` is enforced globally.

## 3. Strict Validation
- **Fail Loudly**: Valid or Invalid. No "Partial Success".
- **Zero Silent Failures**: A typo in a field name must cause a validation error, not be ignored.

## 4. Forward Compatibility
- **Version Safety**: Documents must declare their version.
- **Immutable Schemas**: Released schema versions never change.

## 5. Boring Correctness
- Structure over style.
- Predictability over flexibility.
