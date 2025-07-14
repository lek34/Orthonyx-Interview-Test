
import pytest
import pytest_asyncio
import aiohttp
import asyncio
import json
import uuid
from typing import Dict, Any

# Test configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_PASSWORD = "testpassword123"

@pytest_asyncio.fixture
async def session():
    async with aiohttp.ClientSession() as session:
        yield session

@pytest_asyncio.fixture
async def api_key(session):
    # Generate a unique email for each test run
    unique_email = f"test_{uuid.uuid4().hex}@example.com"
    signup_data = {
        "email": unique_email,
        "password": TEST_PASSWORD
    }
    async with session.post(f"{BASE_URL}/auth/signup", json=signup_data) as response:
        if response.status == 200:
            user_data = await response.json()
            return user_data["api_key"]
        elif response.status == 400:
            # If already exists, try to sign in
            signin_data = {
                "email": unique_email,
                "password": TEST_PASSWORD
            }
            async with session.post(f"{BASE_URL}/auth/signin", json=signin_data) as signin_response:
                assert signin_response.status == 200
                user_data = await signin_response.json()
                return user_data["api_key"]
        else:
            error = await response.text()
            raise Exception(f"Signup failed: {response.status} {error}")

@pytest.mark.asyncio
async def test_health_check(session):
    async with session.get(f"{BASE_URL}/status") as response:
        assert response.status == 200
        data = await response.json()
        assert "status" in data
        assert "database" in data
        assert "openai" in data
        print(f"Health check response: {data}")

@pytest.mark.asyncio
async def test_signup(session):
    unique_email = f"newuser_{uuid.uuid4().hex}@example.com"
    signup_data = {
        "email": unique_email,
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
async def test_signin(session):
    unique_email = f"signin_{uuid.uuid4().hex}@example.com"
    signup_data = {
        "email": unique_email,
        "password": "signinpassword123"
    }
    async with session.post(f"{BASE_URL}/auth/signup", json=signup_data) as response:
        assert response.status == 200
    signin_data = {
        "email": unique_email,
        "password": "signinpassword123"
    }
    async with session.post(f"{BASE_URL}/auth/signin", json=signin_data) as response:
        assert response.status == 200
        data = await response.json()
        assert "api_key" in data
        assert data["email"] == signin_data["email"]
        print(f"Signin response: {data}")

@pytest.mark.asyncio
async def test_symptom_check(session, api_key):
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
async def test_symptom_history(session, api_key):
    headers = {"X-API-Key": api_key}
    async with session.get(f"{BASE_URL}/symptom-history", headers=headers) as response:
        assert response.status == 200
        data = await response.json()
        assert "checks" in data
        assert "total_count" in data
        assert isinstance(data["checks"], list)
        print(f"Symptom history response: {data}")

@pytest.mark.asyncio
async def test_complete_workflow(session):
    unique_email = f"workflow_{uuid.uuid4().hex}@example.com"
    signup_data = {
        "email": unique_email,
        "password": "workflow123"
    }
    async with session.post(f"{BASE_URL}/auth/signup", json=signup_data) as response:
        assert response.status == 200
        user_data = await response.json()
        api_key = user_data["api_key"]
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
    async with session.get(f"{BASE_URL}/symptom-history", headers=headers) as response:
        assert response.status == 200
        history_data = await response.json()
        assert history_data["total_count"] >= 1
        assert len(history_data["checks"]) >= 1
        assert history_data["checks"][0]["id"] == check_id
    print("Complete workflow test passed!")

@pytest.mark.asyncio
async def test_concurrent_requests(session, api_key):
    symptom_data = {
        "age": 35,
        "sex": "male",
        "symptoms": "mild headache and tiredness",
        "duration": "1 day",
        "severity": 3,
        "additional_notes": "stressful week at work"
    }
    headers = {"X-API-Key": api_key}
    async def make_request():
        async with session.post(f"{BASE_URL}/symptom-check", json=symptom_data, headers=headers) as response:
            return response.status, await response.json()
    tasks = [make_request() for _ in range(3)]
    results = await asyncio.gather(*tasks)
    for status, data in results:
        assert status == 200
        assert "id" in data
        assert "analysis" in data
    print(f"Concurrent requests test passed! All {len(results)} requests succeeded.")

@pytest.mark.asyncio
async def test_authentication_errors(session):
    symptom_data = {
        "age": 30,
        "sex": "male",
        "symptoms": "test symptoms",
        "duration": "1 day",
        "severity": 5
    }
    async with session.post(f"{BASE_URL}/symptom-check", json=symptom_data) as response:
        assert response.status == 422  # Missing API key header
    headers = {"X-API-Key": "invalid_key"}
    async with session.post(f"{BASE_URL}/symptom-check", json=symptom_data, headers=headers) as response:
        assert response.status == 401
    print("Authentication error tests passed!")

@pytest.mark.asyncio
async def test_validation_errors(session, api_key):
    headers = {"X-API-Key": api_key}
    invalid_data = {
        "age": 150,  # Invalid age
        "sex": "male",
        "symptoms": "test",
        "duration": "1 day",
        "severity": 5
    }
    async with session.post(f"{BASE_URL}/symptom-check", json=invalid_data, headers=headers) as response:
        assert response.status == 422
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
    pytest.main([__file__, "-v"]) 