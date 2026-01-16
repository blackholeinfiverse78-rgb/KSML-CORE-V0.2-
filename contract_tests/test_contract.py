import pytest
import os
import json
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add validator service to path
sys.path.append(str(Path(__file__).parent.parent / "validator_service"))
from main import app

client = TestClient(app)

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.mark.parametrize("filename", [f for f in os.listdir(EXAMPLES_DIR) if f.endswith(".json")])
def test_contract_examples(filename):
    """
    Validates that:
    - Files starting with 'valid_' pass validation.
    - Files starting with 'invalid_' fail validation.
    """
    path = EXAMPLES_DIR / filename
    data = load_json(path)
    
    print(f"\nTesting {filename}...")
    response = client.post("/validate", json=data)
    assert response.status_code == 200
    res = response.json()
    
    if filename.startswith("valid_"):
        if not res["valid"]:
            pytest.fail(f"Valid example {filename} failed validation: {res.get('errors')}")
        assert res["valid"] is True
        assert res["errors"] == []

    elif filename.startswith("invalid_"):
        if res["valid"]:
            pytest.fail(f"Invalid example {filename} passed validation unexpectedly.")
        assert res["valid"] is False
        assert len(res["errors"]) > 0

def test_determinism():
    valid_file = [f for f in os.listdir(EXAMPLES_DIR) if f.startswith("valid_")][0]
    data = load_json(EXAMPLES_DIR / valid_file)
    
    r1 = client.post("/validate", json=data).json()
    r2 = client.post("/validate", json=data).json()
    
    assert r1 == r2

def test_schema_endpoint():
    response = client.get("/schema")
    assert response.status_code == 200
    schema = response.json()
    assert schema["$id"] == "https://schemas.ksml.io/v0.2/ksml.json"
