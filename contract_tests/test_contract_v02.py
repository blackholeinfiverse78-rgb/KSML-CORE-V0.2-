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

class TestBackwardCompatibility:
    """Ensure v0.1 documents work identically in v0.2 validator"""
    
    def test_v01_examples_unchanged(self):
        """All v0.1 examples must validate identically"""
        v01_files = [f for f in os.listdir(EXAMPLES_DIR) if f.endswith(".json")]
        
        for filename in v01_files:
            path = EXAMPLES_DIR / filename
            data = load_json(path)
            
            # Skip if this is a v0.2 example
            if data.get("ksml_version") == "0.2.0":
                continue
                
            response = client.post("/validate", json=data)
            assert response.status_code == 200
            res = response.json()
            
            if filename.startswith("valid_"):
                assert res["valid"] is True, f"v0.1 valid example {filename} failed: {res.get('errors')}"
                assert res["errors"] == []
                assert res["ksml_version"] == "0.1.0"
                
            elif filename.startswith("invalid_"):
                assert res["valid"] is False, f"v0.1 invalid example {filename} passed unexpectedly"
                assert len(res["errors"]) > 0
    
    def test_v01_error_codes_preserved(self):
        """v0.1 documents must produce identical error codes"""
        # Test missing version
        doc_no_version = {"metadata": {}, "configurations": {}, "steps": []}
        response = client.post("/validate", json=doc_no_version)
        res = response.json()
        
        assert not res["valid"]
        assert any(err["code"] == "KSML_003" for err in res["errors"])
        
        # Test wrong version
        doc_wrong_version = {
            "ksml_version": "1.0.0",
            "metadata": {"id": "test", "author": "test", "title": "test", "created_at": "2024-01-01T00:00:00Z"},
            "configurations": {},
            "steps": [{"name": "test", "action": "test", "parameters": {}}]
        }
        response = client.post("/validate", json=doc_wrong_version)
        res = response.json()
        
        assert not res["valid"]
        assert any(err["code"] == "KSML_003" for err in res["errors"])

class TestV02Features:
    """Test new v0.2 features work correctly"""
    
    def test_v02_version_acceptance(self):
        """v0.2 version should be accepted"""
        doc = {
            "ksml_version": "0.2.0",
            "metadata": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "author": "Test",
                "title": "v0.2 Test",
                "created_at": "2024-01-01T00:00:00Z"
            },
            "configurations": {},
            "steps": [{"name": "test", "action": "test", "parameters": {}}]
        }
        
        response = client.post("/validate", json=doc)
        res = response.json()
        
        assert res["valid"] is True
        assert res["ksml_version"] == "0.2.0"
        assert res["errors"] == []
    
    def test_optional_metadata_fields(self):
        """Test new optional metadata fields"""
        doc = {
            "ksml_version": "0.2.0",
            "metadata": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "author": "Test",
                "title": "v0.2 Test",
                "created_at": "2024-01-01T00:00:00Z",
                "version": "1.0.0",
                "environment": "development",
                "dependencies": [
                    {"name": "test-dep", "version": "1.0.0", "source": "https://example.com"}
                ]
            },
            "configurations": {},
            "steps": [{"name": "test", "action": "test", "parameters": {}}]
        }
        
        response = client.post("/validate", json=doc)
        res = response.json()
        
        assert res["valid"] is True
        assert res["errors"] == []
    
    def test_extensions_block(self):
        """Test extensions block functionality"""
        doc = {
            "ksml_version": "0.2.0",
            "metadata": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "author": "Test",
                "title": "v0.2 Test",
                "created_at": "2024-01-01T00:00:00Z"
            },
            "configurations": {},
            "steps": [{"name": "test", "action": "test", "parameters": {}}],
            "extensions": {
                "x-capabilities": ["retry", "timeout"],
                "x-metadata_extensions": {
                    "schema_url": "https://example.com/schema",
                    "validation_mode": "strict"
                }
            }

        }
        
        response = client.post("/validate", json=doc)
        res = response.json()
        
        assert res["valid"] is True
        assert res["errors"] == []
    
    def test_step_enhancements(self):
        """Test new step-level features"""
        doc = {
            "ksml_version": "0.2.0",
            "metadata": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "author": "Test",
                "title": "v0.2 Test",
                "created_at": "2024-01-01T00:00:00Z"
            },
            "configurations": {},
            "steps": [{
                "name": "enhanced_step",
                "action": "test",
                "parameters": {},
                "timeout_override": 120,
                "retry_policy": {
                    "max_attempts": 3,
                    "backoff_seconds": 5
                },
                "conditions": [
                    {"type": "run_if", "expression": "status == 'ready'"}
                ]
            }]
        }
        
        response = client.post("/validate", json=doc)
        res = response.json()
        
        assert res["valid"] is True
        assert res["errors"] == []

class TestSafetyProtections:
    """Test consumer safety protections"""
    
    def test_document_size_limit(self):
        """Test document size safety limit"""
        # Create a document that's too large
        large_steps = []
        for i in range(150):  # Exceeds 100 step limit
            large_steps.append({
                "name": f"step_{i}",
                "action": "test",
                "parameters": {"data": "x" * 1000}  # Large parameter
            })
        
        doc = {
            "ksml_version": "0.2.0",
            "metadata": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "author": "Test",
                "title": "Large Test",
                "created_at": "2024-01-01T00:00:00Z"
            },
            "configurations": {},
            "steps": large_steps
        }
        
        response = client.post("/validate", json=doc)
        res = response.json()
        
        assert res["valid"] is False
        assert any(err["code"] == "KSML_004" for err in res["errors"])
        assert any("Safety limit exceeded" in err["message"] for err in res["errors"])
    
    def test_step_count_limit(self):
        """Test step count safety limit"""
        doc = {
            "ksml_version": "0.2.0",
            "metadata": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "author": "Test",
                "title": "Many Steps Test",
                "created_at": "2024-01-01T00:00:00Z"
            },
            "configurations": {},
            "steps": [
                {"name": f"step_{i}", "action": "test", "parameters": {}}
                for i in range(101)  # Exceeds 100 limit
            ]
        }
        
        response = client.post("/validate", json=doc)
        res = response.json()
        
        assert res["valid"] is False
        assert any(err["code"] == "KSML_004" for err in res["errors"])
    
    def test_malformed_extensions(self):
        """Test malformed extensions detection"""
        doc = {
            "ksml_version": "0.2.0",
            "metadata": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "author": "Test",
                "title": "Bad Extensions Test",
                "created_at": "2024-01-01T00:00:00Z"
            },
            "configurations": {},
            "steps": [{"name": "test", "action": "test", "parameters": {}}],
            "extensions": {
                "capabilities": ["invalid_capability"]  # Invalid capability
            }
        }
        
        response = client.post("/validate", json=doc)
        res = response.json()
        
        assert res["valid"] is False
        # Should fail schema validation for invalid enum value

class TestVersionHandling:
    """Test version handling logic"""
    
    def test_supported_versions(self):
        """Test all supported versions are accepted"""
        for version in ["0.1.0", "0.2.0"]:
            doc = {
                "ksml_version": version,
                "metadata": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "author": "Test",
                    "title": f"Version {version} Test",
                    "created_at": "2024-01-01T00:00:00Z"
                },
                "configurations": {},
                "steps": [{"name": "test", "action": "test", "parameters": {}}]
            }
            
            response = client.post("/validate", json=doc)
            res = response.json()
            
            assert res["valid"] is True, f"Version {version} should be valid"
            assert res["ksml_version"] == version
    
    def test_unsupported_versions(self):
        """Test unsupported versions are rejected with clear messages"""
        unsupported_versions = ["0.3.0", "1.0.0", "2.0.0", "invalid"]
        
        for version in unsupported_versions:
            doc = {
                "ksml_version": version,
                "metadata": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "author": "Test",
                    "title": f"Version {version} Test",
                    "created_at": "2024-01-01T00:00:00Z"
                },
                "configurations": {},
                "steps": [{"name": "test", "action": "test", "parameters": {}}]
            }
            
            response = client.post("/validate", json=doc)
            res = response.json()
            
            assert res["valid"] is False, f"Version {version} should be invalid"
            assert any(err["code"] == "KSML_003" for err in res["errors"])

class TestDeterminism:
    """Test deterministic behavior"""
    
    def test_same_input_same_output(self):
        """Same input must produce identical output"""
        doc = {
            "ksml_version": "0.2.0",
            "metadata": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "author": "Test",
                "title": "Determinism Test",
                "created_at": "2024-01-01T00:00:00Z"
            },
            "configurations": {},
            "steps": [{"name": "test", "action": "test", "parameters": {}}]
        }
        
        results = []
        for _ in range(5):
            response = client.post("/validate", json=doc)
            results.append(response.json())
        
        # All results should be identical
        first_result = results[0]
        for result in results[1:]:
            assert result == first_result
    
    def test_error_determinism(self):
        """Same invalid input must produce identical errors"""
        doc = {
            "ksml_version": "0.2.0",
            "metadata": {
                "id": "invalid-uuid",  # Invalid UUID format
                "author": "",  # Empty author (violates minLength)
                "title": "Test",
                "created_at": "invalid-date"  # Invalid date format
            },
            "configurations": {},
            "steps": []  # Empty steps (violates minItems)
        }
        
        results = []
        for _ in range(3):
            response = client.post("/validate", json=doc)
            results.append(response.json())
        
        # All results should be identical
        first_result = results[0]
        for result in results[1:]:
            assert result == first_result
            assert not result["valid"]
            assert len(result["errors"]) > 0

class TestSchemaEndpoints:
    """Test schema endpoint functionality"""
    
    def test_default_schema_endpoint(self):
        """Test default schema endpoint returns v0.2"""
        response = client.get("/schema")
        assert response.status_code == 200
        schema = response.json()
        assert schema["$id"] == "https://schemas.ksml.io/v0.2/ksml.json"
    
    def test_versioned_schema_endpoints(self):
        """Test version-specific schema endpoints"""
        # Test v0.1 schema
        response = client.get("/schema/v0.1")
        assert response.status_code == 200
        schema = response.json()
        assert schema["$id"] == "https://schemas.ksml.io/v0.1/ksml.json"
        
        # Test v0.2 schema
        response = client.get("/schema/v0.2")
        assert response.status_code == 200
        schema = response.json()
        assert schema["$id"] == "https://schemas.ksml.io/v0.2/ksml.json"
    
    def test_schema_version_parameter(self):
        """Test schema endpoint with version parameter"""
        response = client.get("/schema?version=0.1.0")
        assert response.status_code == 200
        schema = response.json()
        assert schema["$id"] == "https://schemas.ksml.io/v0.1/ksml.json"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])