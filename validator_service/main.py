from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Depends, Header
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, field_validator
from typing import List, Optional, Any, Dict
import json
import os
import time
import hashlib
import psutil
from pathlib import Path
from collections import defaultdict, deque
import re

# --- Configuration ---
SCHEMA_V01_PATH = Path(__file__).parent.parent / "schema" / "ksml_schema_v0.1.json"
SCHEMA_V02_PATH = Path(__file__).parent.parent / "schema" / "ksml_schema_v0.2.json"
VERSION = "0.2.0"
SUPPORTED_VERSIONS = ["0.1.0", "0.2.0"]
API_KEY = os.getenv("KSML_API_KEY", None)  # Optional authentication
RATE_LIMIT_REQUESTS = 100  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds

# Safety Limits
MAX_DOCUMENT_SIZE = 1024 * 1024  # 1MB
MAX_STEPS = 100
MAX_DEPENDENCIES = 50
MAX_NESTING_DEPTH = 10
MAX_STRING_LENGTH = 10240  # 10KB
MAX_ARRAY_SIZE = 1000
MAX_OBJECT_KEYS = 100

SUSPICIOUS_PATTERNS = [
    r'<script[^>]*>.*?</script>',
    r'javascript:',
    r'data:text/html',
    r'\.\./.*\.\.',
    r'[/\\]etc[/\\]passwd',
    r'[;&|`$]',
    r'rm\s+-rf',
]

# Rate limiting storage
rate_limit_storage = defaultdict(lambda: deque())
schema_cache = {}  # Schema caching

# --- Logging & Metrics ---
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ksml-validator")

METRICS = {
    "total_requests": 0,
    "valid_requests": 0,
    "invalid_requests": 0,
    "errors": 0,
    "rate_limited": 0,
    "memory_usage": 0,
    "start_time": time.time()
}

app = FastAPI(title="KSML Validator Service", version=VERSION)

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)  # Response compression
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Mount static files for UI
static_dir = Path(__file__).parent / "static"
if not static_dir.exists():
    static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# --- Security & Rate Limiting ---
def check_rate_limit(client_ip: str) -> bool:
    now = time.time()
    client_requests = rate_limit_storage[client_ip]
    
    # Remove old requests outside the window
    while client_requests and client_requests[0] < now - RATE_LIMIT_WINDOW:
        client_requests.popleft()
    
    # Check if limit exceeded
    if len(client_requests) >= RATE_LIMIT_REQUESTS:
        return False
    
    # Add current request
    client_requests.append(now)
    return True

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if API_KEY is None:
        return True  # No auth required
    
    if not credentials or credentials.credentials != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True

def sanitize_input(data: dict) -> dict:
    """Basic input sanitization"""
    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="Invalid JSON object")
    
    # Check for suspicious patterns
    data_str = json.dumps(data)
    if len(data_str) > MAX_DOCUMENT_SIZE:  # 1MB limit
        raise HTTPException(status_code=413, detail="Document too large")
    
    return data

# --- Logic: Load Schemas ---
def load_schema(schema_path: Path):
    try:
        if not schema_path.exists():
            raise RuntimeError(f"Schema not found at {schema_path}")
        
        # Check cache first
        cache_key = f"{schema_path}_{schema_path.stat().st_mtime}"
        if cache_key in schema_cache:
            return schema_cache[cache_key]
        
        with open(schema_path, "r") as f:
            schema = json.load(f)
            schema_cache[cache_key] = schema  # Cache the schema
            logger.info(f"Schema loaded and cached from {schema_path}")
            return schema
    except Exception as e:
        logger.critical(f"Failed to load schema: {e}")
        raise e

def get_schema_for_version(version: str) -> dict:
    """Load appropriate schema based on document version"""
    if version == "0.1.0":
        return load_schema(SCHEMA_V01_PATH)
    elif version == "0.2.0":
        return load_schema(SCHEMA_V02_PATH)
    else:
        raise ValueError(f"Unsupported version {version}")

def validate_version(ksml_version: str) -> tuple[bool, str]:
    """Validate version and return acceptance status with reason"""
    if not ksml_version:
        return False, "Missing required field 'ksml_version'"
    
    if ksml_version in SUPPORTED_VERSIONS:
        return True, f"Version {ksml_version} supported"
    
    # Parse and provide specific rejection reason
    try:
        if not isinstance(ksml_version, str):
             return False, f"Invalid version type. Expected string, got {type(ksml_version).__name__}"

        if '.' not in ksml_version:
             return False, f"Invalid version format '{ksml_version}'. Expected semantic version (x.y.z)"

        parts = ksml_version.split('.')
        if len(parts) != 3:
             return False, f"Invalid version format '{ksml_version}'. Expected semantic version (x.y.z)"
             
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        
        if major != 0:
            return False, f"Unsupported major version {major}. Expected 0.x.x"
        
        if minor > 2:
            return False, f"Future version {ksml_version}. Maximum supported: 0.2.x"
        
        return False, f"Unsupported version {ksml_version}. Supported: {', '.join(SUPPORTED_VERSIONS)}"
        
    except ValueError:
        return False, f"Invalid version format '{ksml_version}'. Expected semantic version (x.y.z)"

# Load both schemas at startup
SCHEMA_V01 = load_schema(SCHEMA_V01_PATH)
SCHEMA_V02 = load_schema(SCHEMA_V02_PATH)

# --- Logic: Linting Imports ---
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
try:
    from linting.lint_rules import get_rule, get_rule_v2, Severity
except ImportError:
    # Fallback if linting module is not found or path issues
    def get_rule(code):
         return "ERROR", "Validation Error: {details}" if code == "KSML_100" else "Error {field}"
    def get_rule_v2(code):
         return get_rule(code)
    class Severity:
         ERROR = "ERROR"
         WARNING = "WARNING"


import jsonschema
from jsonschema.validators import validator_for
import json
import re

# --- Models ---
class ValidationError(BaseModel):
    code: str
    message: str
    path: str
    severity: str

class ValidationResult(BaseModel):
    valid: bool
    ksml_version: str
    errors: List[ValidationError]
    warnings: List[str]

class BatchValidationRequest(BaseModel):
    documents: List[dict]
    
    @field_validator('documents')
    @classmethod
    def validate_batch_size(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum 10 documents per batch')
        return v

class BatchValidationResult(BaseModel):
    results: List[ValidationResult]
    summary: Dict[str, int]

# --- Endpoints ---

from starlette.responses import RedirectResponse

@app.get("/")
def root():
    """Redirects to UI for friendly landing."""
    return RedirectResponse(url="/static/index.html")

@app.get("/ui")
def ui():
    """Direct link to UI."""
    return RedirectResponse(url="/static/index.html")

@app.get("/health")
def health():
    # Update memory usage
    METRICS["memory_usage"] = psutil.Process().memory_info().rss / 1024 / 1024  # MB
    
    return {
        "status": "ok", 
        "version": VERSION,
        "uptime_seconds": int(time.time() - METRICS["start_time"]),
        "metrics": {k:v for k,v in METRICS.items() if k != "start_time"},
        "memory_mb": METRICS["memory_usage"],
        "auth_enabled": API_KEY is not None
    }

@app.get("/schema")
def get_schema(version: str = "0.2.0"):
    """Get schema for specified version"""
    try:
        if version == "0.1.0":
            return SCHEMA_V01
        elif version == "0.2.0":
            return SCHEMA_V02
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported schema version: {version}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schema loading error: {str(e)}")

@app.get("/schema/v0.1")
def get_schema_v01():
    """Get v0.1 schema explicitly"""
    return SCHEMA_V01

@app.get("/schema/v0.2")
def get_schema_v02():
    """Get v0.2 schema explicitly"""
    return SCHEMA_V02

@app.post("/validate", response_model=ValidationResult)
async def validate_endpoint(request: Request, document: dict, _: bool = Depends(verify_api_key)):
    client_ip = request.client.host
    
    # Rate limiting
    if not check_rate_limit(client_ip):
        METRICS["rate_limited"] += 1
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Input sanitization
    document = sanitize_input(document)
    
    # Check request size (10MB limit)
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Request too large")
    
    METRICS["total_requests"] += 1
    logger.info(f"Validation request from {client_ip}")
    
    result = await validate_single_document(document, client_ip)
    
    return result

@app.post("/validate/batch", response_model=BatchValidationResult)
async def batch_validate_endpoint(request: Request, batch_request: BatchValidationRequest, _: bool = Depends(verify_api_key)):
    client_ip = request.client.host
    
    # Rate limiting (stricter for batch)
    if not check_rate_limit(client_ip):
        METRICS["rate_limited"] += 1
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    results = []
    summary = {"valid": 0, "invalid": 0, "errors": 0}
    
    for doc in batch_request.documents:
        try:
            # Reuse validation logic
            doc = sanitize_input(doc)
            result = await validate_single_document(doc, client_ip)
            results.append(result)
            
            if result.valid:
                summary["valid"] += 1
            else:
                summary["invalid"] += 1
        except Exception as e:
            summary["errors"] += 1
            results.append(ValidationResult(
                valid=False,
                ksml_version="unknown",
                errors=[ValidationError(code="KSML_001", message=str(e), path="root", severity="ERROR")],
                warnings=[]
            ))
    
    return BatchValidationResult(results=results, summary=summary)

@app.get("/export/{format}")
async def export_results(format: str, results: str = ""):
    """Export validation results in different formats"""
    if format not in ["json", "csv", "xml"]:
        raise HTTPException(status_code=400, detail="Unsupported format")
    
    # Basic export functionality
    if format == "csv":
        return {"content": "code,message,path,severity\n", "media_type": "text/csv"}
    elif format == "xml":
        return {"content": "<?xml version='1.0'?><results></results>", "media_type": "application/xml"}
    else:
        return {"content": "{}", "media_type": "application/json"}

# --- Safety Check Logic ---
def check_nesting_depth(obj: Any, current_depth: int = 0) -> bool:
    if current_depth > MAX_NESTING_DEPTH:
        return False
    
    if isinstance(obj, dict):
        return all(check_nesting_depth(v, current_depth + 1) for v in obj.values())
    elif isinstance(obj, list):
        return all(check_nesting_depth(item, current_depth + 1) for item in obj)
    
    return True

def recursive_item_check(obj: Any, errors: List[ValidationError], path: str):
    """Check for string length, array size, object keys"""
    if isinstance(obj, str):
        if len(obj) > MAX_STRING_LENGTH:
            errors.append(ValidationError(
                code="KSML_004", 
                message=f"Safety limit exceeded: String length {len(obj)} exceeds {MAX_STRING_LENGTH}", 
                path=path, severity="ERROR"))
    elif isinstance(obj, list):
        if len(obj) > MAX_ARRAY_SIZE:
             errors.append(ValidationError(
                code="KSML_004", 
                message=f"Safety limit exceeded: Array size {len(obj)} exceeds {MAX_ARRAY_SIZE}", 
                path=path, severity="ERROR"))
        for i, item in enumerate(obj):
             recursive_item_check(item, errors, f"{path}[{i}]")
    elif isinstance(obj, dict):
        if len(obj) > MAX_OBJECT_KEYS:
             errors.append(ValidationError(
                code="KSML_004", 
                message=f"Safety limit exceeded: Object keys {len(obj)} exceeds {MAX_OBJECT_KEYS}", 
                path=path, severity="ERROR"))
        for k, v in obj.items():
             recursive_item_check(v, errors, f"{path}.{k}")

def check_suspicious_patterns(document: dict) -> List[ValidationError]:
    errors = []
    doc_str = json.dumps(document)
    
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, doc_str, re.IGNORECASE):
            errors.append(ValidationError(
                code="KSML_004",
                message="Safety limit exceeded: Suspicious pattern detected",
                path="root",
                severity="ERROR"
            ))
            break
    return errors

def perform_safety_checks(document: dict) -> List[ValidationError]:
    """Perform v0.2 consumer safety checks"""
    errors = []
    
    # 1. Document Size (already checked in sanitize_input but helpful for clarity if called elsewhere)
    # 2. Step Count
    steps = document.get("steps", [])
    if isinstance(steps, list) and len(steps) > MAX_STEPS:
        errors.append(ValidationError(
            code="KSML_004",
            message=f"Safety limit exceeded: More than {MAX_STEPS} steps not allowed",
            path="steps",
            severity="ERROR"
        ))
    
    # 3. Extensions Type
    extensions = document.get("extensions", {})
    if extensions and not isinstance(extensions, dict):
        errors.append(ValidationError(
            code="KSML_005",
            message="Invalid extension configuration: Extensions must be an object",
            path="extensions",
            severity="ERROR"
        ))

    # 4. Dependency Limit
    metadata = document.get("metadata", {})
    if isinstance(metadata, dict):
        dependencies = metadata.get("dependencies", [])
        if isinstance(dependencies, list) and len(dependencies) > MAX_DEPENDENCIES:
            errors.append(ValidationError(
                 code="KSML_006",
                 message=f"Malformed dependency specification: Too many dependencies ({len(dependencies)}). Max {MAX_DEPENDENCIES}",
                 path="metadata.dependencies",
                 severity="ERROR"
            ))

    # 5. Nesting Depth
    if not check_nesting_depth(document):
         errors.append(ValidationError(
             code="KSML_004",
             message=f"Safety limit exceeded: Nesting depth exceeds {MAX_NESTING_DEPTH}",
             path="root",
             severity="ERROR"
         ))

    # 6. Suspicious Patterns
    errors.extend(check_suspicious_patterns(document))

    # 7. Resource Usage (Strings/Arrays/Keys)
    recursive_item_check(document, errors, "root")

    return errors

async def validate_single_document(document: dict, client_ip: str = "unknown") -> ValidationResult:
    """Unified validation logic"""
    try:
        # 1. Version Check
        doc_ver = document.get("ksml_version")
        version_valid, version_message = validate_version(doc_ver)
        
        if not version_valid:
            sev, msg_template = get_rule("KSML_003")
            METRICS["invalid_requests"] += 1
            if client_ip: logger.warning(f"Version validation failed for {client_ip}: {version_message}")
            return ValidationResult(
                valid=False, 
                ksml_version=str(doc_ver) if doc_ver is not None else "missing", 
                errors=[ValidationError(
                    code="KSML_003", 
                    message=version_message, 
                    path="ksml_version", 
                    severity=sev
                )], 
                warnings=[]
            )
    
        # 2. Get appropriate schema
        try:
            schema = get_schema_for_version(doc_ver)
        except ValueError as e:
            sev, msg_template = get_rule("KSML_001")
            METRICS["errors"] += 1
            logger.error(f"Schema loading error: {e}")
            return ValidationResult(
                valid=False,
                ksml_version=str(doc_ver),
                errors=[ValidationError(
                    code="KSML_001",
                    message=f"Internal System Error: {str(e)}",
                    path="root",
                    severity=sev
                )],
                warnings=[]
            )
        
        errors = []

        # 3. Consumer Safety Checks
        if doc_ver == "0.2.0":
            safety_errors = perform_safety_checks(document)
            errors.extend(safety_errors)

        # 4. Refusal if safety errors
        if errors:
            METRICS["invalid_requests"] += 1
            return ValidationResult(
                valid=False,
                ksml_version=doc_ver,
                errors=errors,
                warnings=[]
            )

        # 5. Schema Validation
        validator_cls = validator_for(schema)
        validator = validator_cls(schema)
        
        raw_errors_iter = list(validator.iter_errors(document))
        raw_errors = sorted(raw_errors_iter, key=lambda e: (str(e.path), e.message))
        
        for err in raw_errors:
            path = ".".join([str(p) for p in err.path]) or "root"
            code = "KSML_100"
            
            # Default details
            details = err.message
            
            if err.validator == "required": 
                code = "KSML_101"
                match = re.search(r"'(.+?)' is a required property", err.message)
                details = match.group(1) if match else err.message
    
            elif err.validator == "type": 
                code = "KSML_102"
                details = err.message 
    
            elif err.validator == "additionalProperties": 
                code = "KSML_103"
                match = re.search(r"\('(.+?)' was unexpected\)", err.message)
                details = match.group(1) if match else "unknown"
            
            # Use appropriate rule getter based on version
            if doc_ver == "0.2.0":
                sev, template = get_rule_v2(code)
            else:
                sev, template = get_rule(code)
            
            # Simple formatting logic
            if code == "KSML_101" or code == "KSML_103":
                final_msg = template.format(field=details)
            elif code == "KSML_100":
                 final_msg = template.format(details=err.message)
            else:
                 final_msg = f"{template} [{err.message}]"
            
            errors.append(ValidationError(code=code, message=final_msg, path=path, severity=sev))
            
        is_valid = len(errors) == 0
        if is_valid:
            METRICS["valid_requests"] += 1
            logger.info(f"Validation success for version {doc_ver}")
        else:
            METRICS["invalid_requests"] += 1
            logger.info(f"Validation failed with {len(errors)} errors for version {doc_ver}")
            
        return ValidationResult(
            valid=is_valid,
            ksml_version=doc_ver,
            errors=errors,
            warnings=[]
        )

    except Exception as e:
        METRICS["errors"] += 1
        logger.error(f"Internal Validator Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal System Error: KSML_001")
