# KSML Consumer Safety Rules v0.2

**Authority**: This document defines mandatory safety protections for KSML consumers.

## 1. Input Size Limits

### Document Size Protection
```python
MAX_DOCUMENT_SIZE = 1024 * 1024  # 1MB
MAX_STEPS = 100
MAX_DEPENDENCIES = 50
MAX_NESTING_DEPTH = 10
```

### Enforcement Rules
- **Hard Limits**: Exceed limit = immediate rejection with KSML_004
- **No Silent Truncation**: Never partially process oversized inputs
- **Clear Messages**: Specific limit exceeded in error message

### Size Check Implementation
```python
def check_document_size(document: dict) -> Optional[ValidationError]:
    doc_str = json.dumps(document, separators=(',', ':'))
    size_bytes = len(doc_str.encode('utf-8'))
    
    if size_bytes > MAX_DOCUMENT_SIZE:
        return ValidationError(
            code="KSML_004",
            message=f"Safety limit exceeded: Document size {size_bytes} bytes exceeds {MAX_DOCUMENT_SIZE} bytes",
            path="root",
            severity="ERROR"
        )
    return None
```

## 2. Structural Safety Checks

### Step Count Limits
- **Maximum Steps**: 100 per document
- **Rationale**: Prevent resource exhaustion in consumers
- **Error Code**: KSML_004

### Dependency Limits
- **Maximum Dependencies**: 50 per document
- **Circular Dependency Detection**: Not implemented (validation only)
- **Error Code**: KSML_006

### Nesting Depth Protection
```python
def check_nesting_depth(obj, current_depth=0, max_depth=MAX_NESTING_DEPTH):
    if current_depth > max_depth:
        return False
    
    if isinstance(obj, dict):
        return all(check_nesting_depth(v, current_depth + 1, max_depth) 
                  for v in obj.values())
    elif isinstance(obj, list):
        return all(check_nesting_depth(item, current_depth + 1, max_depth) 
                  for item in obj)
    
    return True
```

## 3. Malformed Structure Detection

### Shape Validation
- **Required Fields Present**: All mandatory fields exist
- **Type Consistency**: No type confusion attacks
- **Schema Adherence**: Strict validation, no additional properties

### Suspicious Pattern Detection
```python
SUSPICIOUS_PATTERNS = [
    # Potential injection attempts
    r'<script[^>]*>.*?</script>',
    r'javascript:',
    r'data:text/html',
    
    # Potential path traversal
    r'\.\./.*\.\.',
    r'[/\\]etc[/\\]passwd',
    
    # Potential command injection
    r'[;&|`$]',
    r'rm\s+-rf',
]

def check_suspicious_content(document: dict) -> List[ValidationError]:
    errors = []
    doc_str = json.dumps(document)
    
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, doc_str, re.IGNORECASE):
            errors.append(ValidationError(
                code="KSML_004",
                message=f"Safety limit exceeded: Suspicious pattern detected",
                path="root",
                severity="ERROR"
            ))
            break  # One error is enough
    
    return errors
```

## 4. Resource Exhaustion Prevention

### Memory Protection
- **String Length Limits**: Individual strings max 10KB
- **Array Size Limits**: Arrays max 1000 items
- **Object Key Limits**: Objects max 100 keys

### Processing Time Limits
```python
VALIDATION_TIMEOUT = 30  # seconds

@timeout(VALIDATION_TIMEOUT)
def validate_with_timeout(document: dict, schema: dict):
    # Validation logic with timeout protection
    pass
```

### Rate Limiting Integration
- **Per-IP Limits**: 100 requests per minute
- **Burst Protection**: Max 10 concurrent requests per IP
- **Backoff Strategy**: Exponential backoff for repeated violations

## 5. KSML Safety Error Class

### Error Hierarchy
```python
class KSMLSafetyError(Exception):
    """Base class for all KSML safety violations"""
    def __init__(self, code: str, message: str, path: str = "root"):
        self.code = code
        self.message = message
        self.path = path
        super().__init__(f"{code}: {message} at {path}")

class DocumentTooLargeError(KSMLSafetyError):
    def __init__(self, size: int, limit: int):
        super().__init__(
            "KSML_004",
            f"Document size {size} bytes exceeds limit {limit} bytes"
        )

class TooManyStepsError(KSMLSafetyError):
    def __init__(self, count: int, limit: int):
        super().__init__(
            "KSML_004", 
            f"Step count {count} exceeds limit {limit}"
        )

class SuspiciousContentError(KSMLSafetyError):
    def __init__(self, pattern: str):
        super().__init__(
            "KSML_004",
            f"Suspicious pattern detected: {pattern}"
        )
```

## 6. Refusal Mode Implementation

### When to Refuse
1. **Size Violations**: Document or components too large
2. **Structure Violations**: Malformed or suspicious structure
3. **Resource Violations**: Would cause resource exhaustion
4. **Pattern Violations**: Contains suspicious patterns

### Refusal Response Format
```json
{
    "valid": false,
    "ksml_version": "detected_version",
    "errors": [
        {
            "code": "KSML_004",
            "message": "Safety limit exceeded: Specific reason",
            "path": "specific.path",
            "severity": "ERROR"
        }
    ],
    "warnings": [],
    "safety_mode": "REFUSED",
    "reason": "Consumer safety protection activated"
}
```

### No Degraded Modes
- **No Partial Processing**: Either full validation or complete refusal
- **No Silent Filtering**: Never remove content without explicit error
- **No Assumptions**: Never guess intent or fix malformed input

## 7. Implementation Checklist

### Mandatory Safety Checks
- [ ] Document size validation
- [ ] Step count validation  
- [ ] Nesting depth validation
- [ ] Suspicious pattern detection
- [ ] Resource limit enforcement
- [ ] Timeout protection
- [ ] Rate limiting integration

### Error Handling Requirements
- [ ] Specific error codes for each safety violation
- [ ] Clear error messages with actual vs. limit values
- [ ] Proper error path attribution
- [ ] No information leakage in error messages

### Performance Requirements
- [ ] Safety checks complete within 100ms
- [ ] Memory usage bounded during validation
- [ ] No resource leaks on safety violations
- [ ] Graceful degradation under load

---

**IMPLEMENTATION MANDATE**: All KSML v0.2 consumers MUST implement these safety protections to ensure ecosystem security and stability.