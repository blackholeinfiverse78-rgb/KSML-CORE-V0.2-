import pytest
import json
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add validator service to path
sys.path.append(str(Path(__file__).parent.parent / "validator_service"))
from main import app

client = TestClient(app)

class TestFailureModes:
    """Test all failure modes fail loudly, clearly, and deterministically"""
    
    def test_partial_document_failures(self):
        """Test handling of partially malformed documents"""
        
        # Missing required metadata fields
        partial_doc = {
            "ksml_version": "0.2.0",
            "metadata": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                # Missing: author, title, created_at
            },
            "configurations": {},
            "steps": [{"name": "test", "action": "test", "parameters": {}}]
        }
        
        response = client.post("/validate", json=partial_doc)
        res = response.json()
        
        assert response.status_code == 200  # HTTP success but validation failure
        assert res["valid"] is False
        assert len(res["errors"]) >= 2  # Multiple missing fields
        assert all(err["code"] == "KSML_101" for err in res["errors"])
        assert all("Required field missing" in err["message"] for err in res["errors"])
        
        # Verify specific missing fields are reported
        missing_fields = [err["message"] for err in res["errors"]]
        assert any("author" in msg for msg in missing_fields)
        assert any("title" in msg for msg in missing_fields)
        assert any("created_at" in msg for msg in missing_fields)
    
    def test_corrupted_json_structure(self):
        """Test handling of structurally invalid but parseable JSON"""
        
        # Wrong types for required fields
        corrupted_doc = {
            "ksml_version": "0.2.0",  # Valid version to allow body validation
            "metadata": "not_an_object",  # Should be object
            "configurations": [],  # Should be object
            "steps": "not_an_array"  # Should be array
        }
        
        response = client.post("/validate", json=corrupted_doc)
        res = response.json()

        
        assert response.status_code == 200
        assert res["valid"] is False
        assert len(res["errors"]) >= 3  # Multiple type errors
        
        # Check for type mismatch errors
        type_errors = [err for err in res["errors"] if err["code"] == "KSML_102"]
        assert len(type_errors) >= 3  # At least metadata, configurations, steps
    
    def test_unknown_version_handling(self):
        """Test handling of unknown/future versions"""
        
        unknown_versions = ["0.3.0", "1.0.0", "2.5.1", "invalid.version", ""]
        
        for version in unknown_versions:
            doc = {
                "ksml_version": version,
                "metadata": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "author": "Test",
                    "title": "Unknown Version Test",
                    "created_at": "2024-01-01T00:00:00Z"
                },
                "configurations": {},
                "steps": [{"name": "test", "action": "test", "parameters": {}}]
            }
            
            response = client.post("/validate", json=doc)
            res = response.json()
            
            assert response.status_code == 200
            assert res["valid"] is False
            assert len(res["errors"]) == 1
            assert res["errors"][0]["code"] == "KSML_003"
            msg = res["errors"][0]["message"]
            assert any(x in msg for x in ["Unsupported", "Invalid", "Future version", "Missing"])
            assert res["ksml_version"] == str(version)
    
    def test_extension_misuse(self):
        """Test misuse of v0.2 extension features"""
        
        # Invalid extension structure
        bad_extensions_doc = {
            "ksml_version": "0.2.0",
            "metadata": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "author": "Test",
                "title": "Bad Extensions",
                "created_at": "2024-01-01T00:00:00Z"
            },
            "configurations": {},
            "steps": [{"name": "test", "action": "test", "parameters": {}}],
            "extensions": {
                "capabilities": ["invalid_capability", "another_invalid"],  # Invalid enum values
                "metadata_extensions": {
                    "schema_url": "not_a_valid_uri",  # Invalid URI format
                    "validation_mode": "invalid_mode"  # Invalid enum value
                },
                "unknown_extension": "should_not_be_allowed"  # Additional property
            }
        }
        
        response = client.post("/validate", json=bad_extensions_doc)
        res = response.json()
        
        assert response.status_code == 200
        assert res["valid"] is False
        assert len(res["errors"]) >= 1  # At least one validation error (unexpected property or enum)
        
        # Should have schema validation errors for invalid enum values and additional properties
        error_codes = [err["code"] for err in res["errors"]]
        assert "KSML_100" in error_codes or "KSML_103" in error_codes
    
    def test_malformed_dependencies(self):
        """Test malformed dependency specifications"""
        
        bad_deps_doc = {
            "ksml_version": "0.2.0",
            "metadata": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "author": "Test",
                "title": "Bad Dependencies",
                "created_at": "2024-01-01T00:00:00Z",
                "dependencies": [
                    {"name": ""},  # Empty name, missing version
                    {"version": "1.0.0"},  # Missing name
                    {"name": "valid", "version": "1.0.0", "source": "invalid_uri"},  # Invalid URI
                    "not_an_object"  # Wrong type
                ]
            },
            "configurations": {},
            "steps": [{"name": "test", "action": "test", "parameters": {}}]
        }
        
        response = client.post("/validate", json=bad_deps_doc)
        res = response.json()
        
        assert response.status_code == 200
        assert res["valid"] is False
        assert len(res["errors"]) >= 4  # Multiple dependency errors
    
    def test_nested_validation_failures(self):
        """Test deeply nested validation failures"""
        
        nested_failures_doc = {
            "ksml_version": "0.2.0",
            "metadata": {
                "id": "invalid-uuid-format",  # Invalid UUID
                "author": "",  # Empty string (violates minLength)
                "title": "",  # Empty string (violates minLength)
                "created_at": "not-a-date",  # Invalid date format
                "version": "invalid.version.format",  # Invalid semantic version
                "environment": "invalid_environment",  # Invalid enum value
                "dependencies": [
                    {
                        "name": "",  # Empty name
                        "version": "",  # Empty version
                        "source": "not-a-uri"  # Invalid URI
                    }
                ]
            },
            "configurations": {
                "max_retries": -1,  # Below minimum
                "timeout_seconds": 0,  # Below minimum
                "safety_limits": {
                    "max_steps": 0,  # Below minimum
                    "max_document_size_kb": 0  # Below minimum
                }
            },
            "steps": [
                {
                    "name": "",  # Empty name
                    "action": "INVALID-ACTION",  # Invalid pattern (uppercase)
                    "parameters": {
                        "unknown_param": "value"  # Additional property not allowed
                    },
                    "timeout_override": 0,  # Below minimum
                    "retry_policy": {
                        "max_attempts": 0,  # Below minimum
                        "backoff_seconds": 0  # Below minimum
                    },
                    "conditions": [
                        {
                            "type": "invalid_type",  # Invalid enum
                            "expression": ""  # Empty expression
                        }
                    ]
                }
            ]
        }
        
        response = client.post("/validate", json=nested_failures_doc)
        res = response.json()
        
        assert response.status_code == 200
        assert res["valid"] is False
        assert len(res["errors"]) >= 10  # Many validation errors
        
        # Verify errors are properly categorized
        error_codes = [err["code"] for err in res["errors"]]
        assert "KSML_100" in error_codes  # Schema violations
        
        # Verify error paths are specific
        error_paths = [err["path"] for err in res["errors"]]
        assert any("metadata" in path for path in error_paths)
        assert any("configurations" in path for path in error_paths)
        assert any("steps" in path for path in error_paths)
    
    def test_resource_exhaustion_scenarios(self):
        """Test scenarios that could cause resource exhaustion"""
        
        # Extremely deep nesting (should be caught by safety checks)
        deep_nested = {
            "ksml_version": "0.2.0",
            "metadata": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "author": "Test",
                "title": "Deep Nesting Test",
                "created_at": "2024-01-01T00:00:00Z"
            },
            "configurations": {},
            "steps": [
                {
                    "name": "deep_step",
                    "action": "test",
                    "parameters": {
                        "level1": {
                            "level2": {
                                "level3": {
                                    "level4": {
                                        "level5": {
                                            "level6": {
                                                "level7": {
                                                    "level8": {
                                                        "level9": {
                                                            "level10": "deep_value"
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            ]
        }
        
        response = client.post("/validate", json=deep_nested)
        res = response.json()
        
        # Should either validate successfully (if within limits) or fail with safety error
        assert response.status_code == 200
        if not res["valid"]:
            # If it fails, should be due to safety limits or schema violations
            error_codes = [err["code"] for err in res["errors"]]
            assert any(code in ["KSML_004", "KSML_100"] for code in error_codes)
    
    def test_error_message_consistency(self):
        """Test that identical errors produce identical messages"""
        
        # Create identical invalid documents
        invalid_doc = {
            "ksml_version": "0.2.0",
            "metadata": {
                "id": "invalid-uuid",
                "author": "",
                "title": "Test",
                "created_at": "invalid-date"
            },
            "configurations": {},
            "steps": []
        }
        
        # Validate multiple times
        responses = []
        for _ in range(5):
            response = client.post("/validate", json=invalid_doc)
            responses.append(response.json())
        
        # All responses should be identical
        first_response = responses[0]
        for response in responses[1:]:
            assert response == first_response
            assert response["valid"] is False
            assert len(response["errors"]) == len(first_response["errors"])
            
            # Check error ordering is consistent
            for i, error in enumerate(response["errors"]):
                assert error == first_response["errors"][i]
    
    def test_no_silent_failures(self):
        """Test that no failures are silent - everything must be reported"""
        
        # Document with multiple subtle issues
        subtle_issues_doc = {
            "ksml_version": "0.2.0",
            "metadata": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "author": "Test",
                "title": "Subtle Issues",
                "created_at": "2024-01-01T00:00:00Z",
                "tags": [123, True, None]  # Wrong types in array
            },
            "configurations": {
                "max_retries": 11,  # Exceeds maximum
                "timeout_seconds": 3601  # Exceeds maximum
            },
            "steps": [
                {
                    "name": "test",
                    "action": "test_action",
                    "parameters": {},
                    "on_failure": "invalid_option",  # Invalid enum value
                    "timeout_override": 3601,  # Exceeds maximum
                    "retry_policy": {
                        "max_attempts": 6,  # Exceeds maximum
                        "backoff_seconds": 61  # Exceeds maximum
                    }
                }
            ]
        }
        
        response = client.post("/validate", json=subtle_issues_doc)
        res = response.json()
        
        assert response.status_code == 200
        assert res["valid"] is False
        
        # Should report ALL issues, not just the first few
        assert len(res["errors"]) >= 6  # At least 6 distinct issues
        
        # Verify no information is lost in error reporting
        for error in res["errors"]:
            assert error["code"]  # Must have error code
            assert error["message"]  # Must have message
            assert error["path"]  # Must have path
            assert error["severity"]  # Must have severity
    
    def test_deterministic_error_ordering(self):
        """Test that errors are reported in consistent order"""
        
        multi_error_doc = {
            "ksml_version": "0.2.0",
            "metadata": {
                "id": "invalid",  # Error 1: Invalid UUID
                "author": "",  # Error 2: Empty author
                "title": "",  # Error 3: Empty title
                "created_at": "invalid"  # Error 4: Invalid date
            },
            "configurations": {
                "max_retries": -1,  # Error 5: Below minimum
                "timeout_seconds": 0  # Error 6: Below minimum
            },
            "steps": []  # Error 7: Empty array (violates minItems)
        }
        
        # Validate multiple times
        error_orders = []
        for _ in range(3):
            response = client.post("/validate", json=multi_error_doc)
            res = response.json()
            error_order = [(err["path"], err["code"], err["message"]) for err in res["errors"]]
            error_orders.append(error_order)
        
        # All error orders should be identical
        first_order = error_orders[0]
        for order in error_orders[1:]:
            assert order == first_order, "Error ordering must be deterministic"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])