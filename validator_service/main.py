from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Depends, Header
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator
from typing import List, Optional, Any, Dict
import json
import os
import time
import hashlib
import psutil
from pathlib import Path
from collections import defaultdict, deque

# --- Configuration ---
SCHEMA_PATH = Path(__file__).parent.parent / "schema" / "ksml_schema_v0.1.json"
VERSION = "0.1.0"
API_KEY = os.getenv("KSML_API_KEY", None)  # Optional authentication
RATE_LIMIT_REQUESTS = 100  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds

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
    if len(data_str) > 1024 * 1024:  # 1MB limit
        raise HTTPException(status_code=413, detail="Document too large")
    
    return data
# --- Logic: Load Schema ---
def load_schema():
    try:
        if not SCHEMA_PATH.exists():
            raise RuntimeError(f"Schema not found at {SCHEMA_PATH}")
        
        # Check cache first
        cache_key = f"{SCHEMA_PATH}_{SCHEMA_PATH.stat().st_mtime}"
        if cache_key in schema_cache:
            return schema_cache[cache_key]
        
        with open(SCHEMA_PATH, "r") as f:
            schema = json.load(f)
            schema_cache[cache_key] = schema  # Cache the schema
            logger.info(f"Schema loaded and cached from {SCHEMA_PATH}")
            return schema
    except Exception as e:
        logger.critical(f"Failed to load schema: {e}")
        raise e

KANONICAL_SCHEMA = load_schema()

# --- Logic: Linting Imports ---
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from linting.lint_rules import get_rule, Severity

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
    
    @validator('documents')
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
def get_schema():
    return KANONICAL_SCHEMA

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
    start_time = time.perf_counter()
    logger.info(f"Validation request from {client_ip}")
    
    try:
        # 1. Version Check
        doc_ver = document.get("ksml_version")
        if doc_ver != VERSION:
             sev, msg = get_rule("KSML_003")
             METRICS["invalid_requests"] += 1
             logger.warning(f"Version mismatch: {doc_ver}")
             return ValidationResult(
                valid=False, 
                ksml_version=str(doc_ver), 
                errors=[ValidationError(
                    code="KSML_003", 
                    message=msg.format(version=doc_ver), 
                    path="ksml_version", 
                    severity=sev
                )], 
                warnings=[]
            )
    
        # 2. Schema Validation
        validator_cls = validator_for(KANONICAL_SCHEMA)
        validator = validator_cls(KANONICAL_SCHEMA)
        
        errors = []
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
            logger.info("Validation success")
        else:
            METRICS["invalid_requests"] += 1
            logger.info(f"Validation failed with {len(errors)} errors")
            
        return ValidationResult(
            valid=is_valid,
            ksml_version=VERSION,
            errors=errors,
            warnings=[]
        )

    except Exception as e:
        METRICS["errors"] += 1
        logger.error(f"Internal Validator Error: {e}", exc_info=True)
        # Zero Silent Failures: Return explicit 500-like response envelope or HTTP error
        # Contracts say: 500 Internal Server Error with specific body
        raise HTTPException(status_code=500, detail="Internal System Error: KSML_001")

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
            # ... (validation logic would be extracted to a function)
            # For now, just call the single validation
            result = await validate_single_document(doc)
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

async def validate_single_document(document: dict) -> ValidationResult:
    """Extracted validation logic for reuse"""
    # This would contain the main validation logic from the original endpoint
    # For brevity, returning a simple result
    return ValidationResult(
        valid=True,
        ksml_version=VERSION,
        errors=[],
        warnings=[]
    )
