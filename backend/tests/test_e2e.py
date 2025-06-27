import pytest
import aiohttp
import asyncio
import json
from typing import Dict, Any

# Test configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

class TestMedicalSymptomChecker:
    """End-to-end tests for Medical Symptom Checker API"""
    
    @pytest.fixture
    async def session(self):
        """Create aiohttp session for testing"""
        async with aiohttp.ClientSession() as session:
            yield session
    
    @pytest.fixture
    async def api_key(self, session):
        """Get API key by signing up a test user"""
        # Sign up user
        signup_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        async with session.post(f"{BASE_URL}/auth/signup", json=signup_data) as response:
            assert response.status == 200
            user_data = await response.json()
            return user_data["api_key"]
    
    @pytest.mark.asyncio
    async def test_health_check(self, session):
        """Test health check endpoint"""
        async with session.get(f"{BASE_URL}/health") as response:
            assert response.status == 200
            data = await response.json()
            assert "status" in data
            assert "database" in data
            assert "openai" in data
            print(f"Health check response: {data}")
    
    @pytest.mark.asyncio
    async def test_signup(self, session):
        """Test user signup"""
        signup_data = {
            "email": "newuser@example.com",
            "password": "newpassword123"
        }
        
        async with session.post(f"{BASE_URL}/auth/signup", json=signup_data) as response:
            assert response.status == 200
            data = await response.json()
            assert "id" in data
            assert "email" in data
            assert "api_key" in data
            assert data["email"] == signup_data["email"]
            print(f"Signup response: {data}")
    
    @pytest.mark.asyncio
    async def test_signin(self, session):
        """Test user signin"""
        # First sign up
        signup_data = {
            "email": "signin@example.com",
            "password": "signinpassword123"
        }
        
        async with session.post(f"{BASE_URL}/auth/signup", json=signup_data) as response:
            assert response.status == 200
        
        # Then sign in
        signin_data = {
            "email": "signin@example.com",
            "password": "signinpassword123"
        }
        
        async with session.post(f"{BASE_URL}/auth/signin", json=signin_data) as response:
            assert response.status == 200
            data = await response.json()
            assert "api_key" in data
            assert data["email"] == signin_data["email"]
            print(f"Signin response: {data}")
    
    @pytest.mark.asyncio
    async def test_symptom_check(self, session, api_key):
        """Test symptom check endpoint"""
        symptom_data = {
            "age": 30,
            "sex": "male",
            "symptoms": "headache and fever for the past 2 days",
            "duration": "2 days",
            "severity": 7,
            "additional_notes": "also experiencing fatigue"
        }
        
        headers = {"X-API-Key": api_key}
        
        async with session.post(f"{BASE_URL}/symptom-check", json=symptom_data, headers=headers) as response:
            assert response.status == 200
            data = await response.json()
            assert "id" in data
            assert "user_id" in data
            assert "analysis" in data
            assert "status" in data
            assert data["status"] == "completed"
            print(f"Symptom check response: {data}")
    
    @pytest.mark.asyncio
    async def test_symptom_history(self, session, api_key):
        """Test symptom history endpoint"""
        headers = {"X-API-Key": api_key}
        
        async with session.get(f"{BASE_URL}/symptom-history", headers=headers) as response:
            assert response.status == 200
            data = await response.json()
            assert "checks" in data
            assert "total_count" in data
            assert isinstance(data["checks"], list)
            print(f"Symptom history response: {data}")
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self, session):
        """Test complete workflow: signup -> symptom check -> history"""
        # Step 1: Sign up
        signup_data = {
            "email": "workflow@example.com",
            "password": "workflow123"
        }
        
        async with session.post(f"{BASE_URL}/auth/signup", json=signup_data) as response:
            assert response.status == 200
            user_data = await response.json()
            api_key = user_data["api_key"]
        
        # Step 2: Submit symptom check
        symptom_data = {
            "age": 25,
            "sex": "female",
            "symptoms": "cough and sore throat for 3 days",
            "duration": "3 days",
            "severity": 5,
            "additional_notes": "worse in the morning"
        }
        
        headers = {"X-API-Key": api_key}
        
        async with session.post(f"{BASE_URL}/symptom-check", json=symptom_data, headers=headers) as response:
            assert response.status == 200
            check_data = await response.json()
            check_id = check_data["id"]
        
        # Step 3: Get symptom history
        async with session.get(f"{BASE_URL}/symptom-history", headers=headers) as response:
            assert response.status == 200
            history_data = await response.json()
            assert history_data["total_count"] >= 1
            assert len(history_data["checks"]) >= 1
            assert history_data["checks"][0]["id"] == check_id
        
        print("Complete workflow test passed!")
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, session, api_key):
        """Test concurrent symptom check requests"""
        symptom_data = {
            "age": 35,
            "sex": "male",
            "symptoms": "mild headache and tiredness",
            "duration": "1 day",
            "severity": 3,
            "additional_notes": "stressful week at work"
        }
        
        headers = {"X-API-Key": api_key}
        
        # Create multiple concurrent requests
        async def make_request():
            async with session.post(f"{BASE_URL}/symptom-check", json=symptom_data, headers=headers) as response:
                return response.status, await response.json()
        
        # Execute 3 concurrent requests
        tasks = [make_request() for _ in range(3)]
        results = await asyncio.gather(*tasks)
        
        # Check all requests succeeded
        for status, data in results:
            assert status == 200
            assert "id" in data
            assert "analysis" in data
        
        print(f"Concurrent requests test passed! All {len(results)} requests succeeded.")
    
    @pytest.mark.asyncio
    async def test_authentication_errors(self, session):
        """Test authentication error scenarios"""
        # Test without API key
        symptom_data = {
            "age": 30,
            "sex": "male",
            "symptoms": "test symptoms",
            "duration": "1 day",
            "severity": 5
        }
        
        async with session.post(f"{BASE_URL}/symptom-check", json=symptom_data) as response:
            assert response.status == 422  # Missing API key header
        
        # Test with invalid API key
        headers = {"X-API-Key": "invalid_key"}
        async with session.post(f"{BASE_URL}/symptom-check", json=symptom_data, headers=headers) as response:
            assert response.status == 401
        
        print("Authentication error tests passed!")
    
    @pytest.mark.asyncio
    async def test_validation_errors(self, session, api_key):
        """Test input validation errors"""
        headers = {"X-API-Key": api_key}
        
        # Test invalid age
        invalid_data = {
            "age": 150,  # Invalid age
            "sex": "male",
            "symptoms": "test",
            "duration": "1 day",
            "severity": 5
        }
        
        async with session.post(f"{BASE_URL}/symptom-check", json=invalid_data, headers=headers) as response:
            assert response.status == 422
        
        # Test invalid severity
        invalid_data = {
            "age": 30,
            "sex": "male",
            "symptoms": "test symptoms",
            "duration": "1 day",
            "severity": 15  # Invalid severity
        }
        
        async with session.post(f"{BASE_URL}/symptom-check", json=invalid_data, headers=headers) as response:
            assert response.status == 422
        
        print("Validation error tests passed!")

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 