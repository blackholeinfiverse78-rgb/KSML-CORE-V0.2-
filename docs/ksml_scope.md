# KSML Scope Definition

**Version**: 0.1.0

## 1. Definition
KSML (Knowledge System Markup Language) is a strict, logic-less schema contract for defining system operations.

## 2. In Scope (What KSML IS)
- **Structure**: A JSON-based format defined by a canonical JSON Schema Draft-07 file.
- **Validation**: A deterministic pass/fail check against the schema.
- **Contracts**: Explicit API input/output definitions for validation tools.

## 3. Out of Scope (What KSML is NOT)
- **Execution**: KSML does not define *how* steps are executed.
- **Orchestration**: KSML does not define control flow, retries (beyond config fields), or state management.
- **Cognition**: KSML contains no AI or "agentic" logic. It is data.
- **Transport**: KSML does not define how it is stored or transmitted.

## 4. Boundaries
The responsibility of KSML Core ends at the **Validation Result**. `valid: true` means the contract is met. Usability of the content is the consumer's responsibility.
