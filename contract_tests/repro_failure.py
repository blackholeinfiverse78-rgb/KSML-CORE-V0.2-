import sys
import json
from pathlib import Path
from fastapi.testclient import TestClient

# Add validator_service to sys.path
sys.path.append(str(Path(__file__).parent.parent / "validator_service"))
from main import app

client = TestClient(app)

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
INVALID_EX = EXAMPLES_DIR / "valid_example.ksml.json"

print(f"Loading {INVALID_EX}")
with open(INVALID_EX, "r") as f:
    data = json.load(f)

print("Sending request...")
response = client.post("/validate", json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

if response.json()["valid"] is False:
    print("FAILURE: Valid Document was rejected!")
    # print errors
    print(response.json().get("errors"))
    exit(1)
else:
    print("SUCCESS: Document was accepted.")
