import pytest
import os
import json
from pathlib import Path
from fastapi.testclient import TestClient
# We need to import app from sibling validator_service
import sys
# Add validator_service to path for import
sys.path.append(str(Path(__file__).parent.parent / "validator_service"))
from main import app

client = TestClient(app)

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

@pytest.mark.parametrize("filename", os.listdir(EXAMPLES_DIR))
def test_examples(filename):
    """
    Contract: 
    - invalid_*.json MUST fail.
    - valid_*.json MUST pass.
    """
    if not filename.endswith(".json"):
        return

    path = EXAMPLES_DIR / filename
    data = load_json(path)
    
    response = client.post("/validate", json=data)
    assert response.status_code == 200
    res = response.json()
    
    if filename.startswith("valid_"):
        assert res["valid"] is True, f"{filename} should be valid but failed: {res.get('errors')}"
    elif filename.startswith("invalid_"):
        # print(f"DEBUG RESPONSE for {filename}: {res}")
        assert res["valid"] is False, f"{filename} should be invalid but passed."
        assert len(res["errors"]) > 0


def test_determinism():
    """
    Contract: Determinism check.
    """
    valid_file = [f for f in os.listdir(EXAMPLES_DIR) if "valid_" in f][0]
    data = load_json(EXAMPLES_DIR / valid_file)
    
    r1 = client.post("/validate", json=data).json()
    r2 = client.post("/validate", json=data).json()
    assert r1 == r2

if __name__ == "__main__":
    print("Running Contract Tests...")
    # Manual run logic if needed
    for f in os.listdir(EXAMPLES_DIR):
        if not f.endswith(".json"): continue
        print(f"Testing {f}...")
        test_examples(f)
        print("PASS")
    test_determinism()
    print("Determinism PASS")
