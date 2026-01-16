# KSML v0.2 Migration Notes

## Why v0.2 Exists?
KSML v0.1 established the foundation of **Strict Determinism**. However, real-world usage identified gaps that led to "shadow patterns" (e.g., hiding metadata in strings, implicit timeout expectations).

v0.2 formalizes these needs without breaking the core contract:
1.  **Safety**: Preventing "DoS by JSON" via strict limits.
2.  **Extensibility**: Allowing vendor-specific data (`extensions`) without polluting the spec.
3.  **Robustness**: Explicit operational controls (`retry_policy`, `timeout`) to replace implicit behavior.

## Migration Strategy

### Phase 1: Validator Upgrade (Day 1)
*   Deploy v0.2 Validator Service.
*   **Impact**: Zero. It accepts v0.1 documents identically.
*   **Benefit**: Immediate protection against malformed/oversized payloads (Safety Layer is active for v0.2, valid v0.1 docs pass).

### Phase 2: Pilot Adoption (Day 2-7)
*   Select non-critical operations.
*   Update `ksml_version` to `"0.2.0"`.
*   Utilize `extensions` for any custom metadata currently stored in `description` fields.
*   Utilize `dependencies` to declare external links explicitly.

### Phase 3: Operational Hardening (Day 8+)
*   Apply `retry_policy` to flaky steps.
*   Set `timeout_override` for long-running steps.
*   Enforce `environment: "production"` checks in your CI/CD pipeline.

## Breaking Changes?
**None.**
v0.2 is strictly additive.
*   `v0.1` document + `v0.2` validator = **PASS**
*   `v0.2` document + `v0.1` validator = **FAIL** (Expected: Major version mismatch / Unknown fields).

## Common Pitfalls
1.  **Extension Keys**: You usually forget the `x-` prefix.
    *   *Wrong*: `"my-tool": {...}`
    *   *Right*: `"x-my-tool": {...}`
2.  **Safety Limits**: If you generated 500-step KSML files programmatically, they will now fail.
    *   *Fix*: Split logic into multiple files or sub-processes (if supported by your orchestrator).
3.  **Dependency Versioning**: `dependencies` items can now trigger validation errors if fields are wrong.