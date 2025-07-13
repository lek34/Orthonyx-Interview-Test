# Medical Symptom Checker API

A FastAPI application for analyzing medical symptoms using OpenAI's GPT-4o model. This project demonstrates async programming patterns, SQLAlchemy ORM, and AI integration.

## Features

- ✅ User authentication with API keys
- ✅ Async symptom analysis using OpenAI GPT-4o
- ✅ MySQL database with SQLAlchemy ORM
- ✅ Automatic database table creation
- ✅ Complete end-to-end testing
- ✅ Concurrent request handling
- ✅ Proper error handling and validation

## Prerequisites

- Python 3.8+
- MySQL Server
- OpenAI API key

## Setup Instructions

### 1. Clone and Setup Environment

```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows Command Prompt:
.\venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

1. **Install MySQL** (if not already installed)
   - Download from: https://dev.mysql.com/downloads/mysql/
   - Or use Docker: `docker run --name mysql -e MYSQL_ROOT_PASSWORD=your_password -p 3306:3306 -d mysql:8.0`

2. **Database Will Be Create Automatically** (tables will be created automatically)
   ```sql
   CREATE DATABASE medical_symptom_checker;
   ```

### 4. Environment Configuration

1. **Copy the example environment file:**
   ```bash
   copy env.example .env
   ```

2. **Edit `.env` file with your settings:**
   ```env
   # Database Configuration
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_NAME=medical_symptom_checker

   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key_here

   # Server Configuration
   HOST=127.0.0.1
   PORT=8000
   ```

### 5. Run the Application

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run the application (tables will be created automatically)
uvicorn app.main:app --reload
```

The API will be available at: http://127.0.0.1:8000

## 🚀 **Automatic Database Features**

- **Auto Table Creation**: Tables are created automatically when the app starts
- **SQLAlchemy ORM**: Clean, type-safe database operations
- **Async Database**: All database operations are async
- **Automatic Migrations**: Schema changes are handled automatically

## API Documentation

- **Interactive API docs**: http://127.0.0.1:8000/docs
- **Alternative API docs**: http://127.0.0.1:8000/redoc
- **Status check**: http://127.0.0.1:8000/status

## API Endpoints

### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/signin` - User login

### Symptom Analysis
- `POST /symptom-check` - Submit symptoms for analysis (requires API key)
- `GET /symptom-history` - Get user's symptom check history (requires API key)

### Status
- `GET /status` - Status check endpoint

## Usage Examples

### 1. User Registration
```bash
curl -X POST "http://127.0.0.1:8000/auth/signup" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "password": "password123"
     }'
```

### 2. User Login
```bash
curl -X POST "http://127.0.0.1:8000/auth/signin" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "password": "password123"
     }'
```

### 3. Symptom Check (requires API key)
```bash
curl -X POST "http://127.0.0.1:8000/symptom-check" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your_api_key_here" \
     -d '{
       "age": 30,
       "sex": "male",
       "symptoms": "headache and fever for 2 days",
       "duration": "2 days",
       "severity": 7,
       "additional_notes": "also experiencing fatigue"
     }'
```

### 4. Get Symptom History
```bash
curl -X GET "http://127.0.0.1:8000/symptom-history" \
     -H "X-API-Key: your_api_key_here"
```

## Testing

### Run End-to-End Tests

```bash
# Make sure the application is running first
uvicorn app.main:app --reload

# In another terminal, run tests
cd backend
.\venv\Scripts\Activate.ps1
pytest tests/test_e2e.py -v
```

### Test Coverage

The tests cover:
- ✅ Status check endpoint
- ✅ User registration and login
- ✅ Symptom analysis workflow
- ✅ Symptom history retrieval
- ✅ Concurrent request handling
- ✅ Authentication error scenarios
- ✅ Input validation errors
- ✅ Complete end-to-end workflow

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration and environment variables
│   ├── models.py            # Pydantic models + SQLAlchemy models
│   ├── database.py          # SQLAlchemy database setup
│   ├── auth.py              # Authentication service
│   └── openai_service.py    # OpenAI integration
├── tests/
│   ├── __init__.py
│   └── test_e2e.py          # End-to-end tests
├── requirements.txt         # Python dependencies
├── main.py                 # Application entry point
├── README.md               # This file
├── QUICKSTART.md           # Quick setup guide
├── .gitignore              # Git ignore rules
└── env.example             # Environment variables example
```

## SQLAlchemy ORM Features

- **Automatic Table Creation**: Tables are created on app startup
- **Type Safety**: Full type hints and validation
- **Async Operations**: All database operations are async
- **Relationships**: Proper foreign key relationships
- **Auto-Incrementing IDs**: Clean integer primary keys (1, 2, 3...)
- **Migrations Ready**: Easy to add Alembic migrations later

## Async Programming Features

- **Concurrent Request Handling**: Multiple symptom checks can be processed simultaneously
- **Async Database Operations**: All database queries use async/await patterns
- **Async OpenAI Integration**: Non-blocking API calls with retry logic
- **Proper Error Handling**: Graceful handling of API failures and timeouts

## Security Features

- **API Key Authentication**: Secure API key-based authentication
- **Password Hashing**: Bcrypt password hashing
- **Environment Variables**: No hardcoded secrets
- **Input Validation**: Comprehensive request validation
- **Error Handling**: Proper HTTP status codes

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure MySQL is running
   - Check database credentials in `.env`
   - Verify database exists (tables will be created automatically)

2. **OpenAI API Error**
   - Check your OpenAI API key in `.env`
   - Ensure you have sufficient credits
   - Verify internet connection

3. **Import Errors**
   - Make sure virtual environment is activated
   - Run `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

4. **Port Already in Use**
   - Change port in `.env` file
   - Or kill existing process: `netstat -ano | findstr :8000`

### Getting Help

- Check the logs for detailed error messages
- Verify all environment variables are set correctly
- Ensure all dependencies are installed
- Test database connection manually

## Development

### Adding New Features

1. Create new models in `app/models.py`
2. Add database operations using SQLAlchemy ORM
3. Create new endpoints in `app/main.py`
4. Add tests in `tests/test_e2e.py`

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Add docstrings to functions
- Handle errors gracefully

## License

This project is for educational and demonstration purposes. 