# KSML Versioning Rules

**Authority**: This document defines the laws of mutation for KSML.

## 1. The Core Law of Versioning
**NO CHANGE SHALL BREAK AN EXISTNG VALID DOCUMENT WITHOUT A MAJOR VERSION INCREMENT.**

## 2. Semantic Versioning Specification (`Major.Minor.Patch`)

### Major (`X.0.0`) - The "Breaking" Increment
- **Trigger**: Any change that renders a previously valid document invalid.
- **Action**: Increment `X`. Reset `Minor` and `Patch` to 0.
- **Example**: 
    - Making an optional field required.
    - Removing a field entirely.
    - Reducing the allowed range of a number.
    - Changing a type (e.g., string to int).

### Minor (`0.X.0`) - The "feature" Increment
- **Trigger**: Adding new capabilities that are strictly optional. Old documents remain valid.
- **Action**: Increment `Minor`. Reset `Patch` to 0.
- **Constraint**: `additionalProperties` must remain `false`. New fields must be explicitly added to the schema.
- **Example**:
    - Adding a new optional field.
    - Adding a new allowed value to an ENUM.
    - Relaxing a constraint (e.g., increasing max length).

### Patch (`0.0.X`) - The "Fix" Increment
- **Trigger**: Zero logic changes. Only clarifications or non-functional fixes.
- **Action**: Increment `Patch`.
- **Example**:
    - Fixing a typo in a description (NOT a field name).
    - Adding examples to documentation.

## 3. Version Declaration Contract
Every KSML document **MUST** declare its target version in the root object.

```json
{
  "ksml_version": "0.1.0",
  ...
}
```

- **Consumer Rule**: A consumer (Validator/Parser) designed for `v1.2.0` MUST accept `v1.0.0`, `v1.1.0`.
- **Rejection Rule**: A consumer MUST reject any `ksml_version` with a Major component different from its own supported Major version (e.g., `v2.0.0` parser rejects `v1.0.0`).

## 4. Stability Guarantees
- **Immutability**: Once a version tag (e.g., `v0.1.0`) is pushed to the repository, the artifacts for that version (schema, docs) are **READ-ONLY**.
- **Freeze**: `v0.1.0` is the frozen baseline. All future changes are diffs against this baseline.
