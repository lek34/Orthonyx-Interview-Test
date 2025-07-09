# Quick Start Guide

Get the Medical Symptom Checker API running in 5 minutes!

## Prerequisites

- Python 3.8+
- MySQL Server running
- OpenAI API key

## Quick Setup

### 1. Install Dependencies
```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
```

### 2. Setup Environment
```bash
copy env.example .env
```

Edit `.env` file with your settings:
```env
DB_PASSWORD=your_mysql_password
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Setup Database
```sql
-- Connect to MySQL and create database only
CREATE DATABASE medical_symptom_checker;
```
**Note**: Tables will be created automatically when you start the app!

### 4. Run the Application
```bash
uvicorn app.main:app --reload
```

Visit: http://127.0.0.1:8000/docs

## 🚀 **What's New with ORM**

- **Automatic Table Creation**: No need to run SQL scripts manually
- **Type-Safe Database Operations**: SQLAlchemy ORM with full type hints
- **Async Database**: All operations are async for better performance
- **Clean Code**: No more raw SQL queries

## Quick Test

### 1. Register a User
```bash
curl -X POST "http://127.0.0.1:8000/auth/signup" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "password123"}'
```

### 2. Submit Symptoms
```bash
curl -X POST "http://127.0.0.1:8000/symptom-check" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: YOUR_API_KEY_FROM_STEP_1" \
     -d '{
       "age": 30,
       "sex": "male",
       "symptoms": "headache and fever for 2 days",
       "duration": "2 days",
       "severity": 7,
       "additional_notes": "also experiencing fatigue"
     }'
```

### 3. Check History
```bash
curl -X GET "http://127.0.0.1:8000/symptom-history" \
     -H "X-API-Key: YOUR_API_KEY_FROM_STEP_1"
```

## Run Tests
```bash
pytest tests/test_e2e.py -v
```

## Database Schema (Auto-Created)

The following tables are created automatically:

```sql
-- Users table
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    api_key VARCHAR(64) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Symptom checks table
CREATE TABLE symptom_checks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    age INT NOT NULL,
    sex VARCHAR(10) NOT NULL,
    symptoms TEXT NOT NULL,
    duration VARCHAR(100) NOT NULL,
    severity INT NOT NULL,
    additional_notes TEXT,
    analysis TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

That's it! Your Medical Symptom Checker API is ready to use! 🎉

**No manual table creation needed - everything is automatic!** 