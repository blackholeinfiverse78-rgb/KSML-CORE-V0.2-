# KSML Quick Start Guide

## 1. Start the Service (30 seconds)

```bash
cd ksml-core-v0.1/validator_service
python run_ui.py
```

## 2. Open Web UI

Browser: **http://localhost:8002**

## 3. Test Validation

1. **Click "Random Sample"** - Loads realistic KSML data
2. **Click "Validate"** - See results instantly
3. **Try "Load Invalid Example"** - See error handling

## 4. API Usage

```bash
# Validate a document
curl -X POST http://localhost:8002/validate \
  -H "Content-Type: application/json" \
  -d '{"ksml_version":"0.1.0","metadata":{"id":"test","author":"me","title":"test","created_at":"2024-01-01T00:00:00Z"},"configurations":{},"steps":[{"name":"test","action":"test","parameters":{}}]}'

# Get schema
curl http://localhost:8002/schema

# Health check
curl http://localhost:8002/health
```

## 5. Common Errors

- **KSML_101**: Missing required field → Add the field
- **KSML_102**: Wrong type → Fix `"123"` to `123`
- **KSML_103**: Unknown field → Remove extra field

**That's it! You're ready to validate KSML documents.**