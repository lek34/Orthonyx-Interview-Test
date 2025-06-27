import logging
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .database import get_db, init_db, close_db
from .auth import auth_service
from .openai_service import openai_service
from .models import (
    UserSignup, UserSignin, UserResponse,
    SymptomCheckRequest, SymptomCheckResponse, SymptomHistoryResponse,
    User, SymptomCheck
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    try:
        await init_db()
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    await close_db()
    logger.info("Application shutdown complete")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Medical Symptom Checker API",
    description="A FastAPI application for analyzing medical symptoms using OpenAI",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get current user from API key
async def get_current_user(
    api_key: str = Header(..., alias="X-API-Key"),
    db: AsyncSession = Depends(get_db)
):
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    user = await auth_service.get_user_by_api_key(api_key, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return user

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        async for db in get_db():
            result = await db.execute(select(1))
            result.scalar()
            break
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    # Check OpenAI connection
    openai_status = "healthy" if await openai_service.health_check() else "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" and openai_status == "healthy" else "unhealthy",
        "database": db_status,
        "openai": openai_status,
        "timestamp": datetime.utcnow().isoformat()
    }

# Authentication endpoints
@app.post("/auth/signup", response_model=UserResponse)
async def signup(user_data: UserSignup, db: AsyncSession = Depends(get_db)):
    """User registration endpoint"""
    try:
        user = await auth_service.create_user(user_data, db)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/auth/signin", response_model=UserResponse)
async def signin(user_data: UserSignin, db: AsyncSession = Depends(get_db)):
    """User login endpoint"""
    try:
        user = await auth_service.authenticate_user(user_data, db)
        return user
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Signin error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Symptom check endpoints
@app.post("/symptom-check", response_model=SymptomCheckResponse)
async def symptom_check(
    symptom_data: SymptomCheckRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit symptoms for analysis"""
    try:
        # Analyze symptoms using OpenAI
        analysis = await openai_service.analyze_symptoms(symptom_data)
        
        # Create symptom check record
        symptom_check_obj = SymptomCheck(
            user_id=current_user.id,
            age=symptom_data.age,
            sex=symptom_data.sex,
            symptoms=symptom_data.symptoms,
            duration=symptom_data.duration,
            severity=symptom_data.severity,
            additional_notes=symptom_data.additional_notes,
            analysis=analysis,
            status="completed"
        )
        
        # Save to database
        db.add(symptom_check_obj)
        await db.commit()
        await db.refresh(symptom_check_obj)
        
        # Return response
        return SymptomCheckResponse(
            id=symptom_check_obj.id,  # type: ignore
            user_id=symptom_check_obj.user_id,  # type: ignore
            timestamp=symptom_check_obj.created_at,  # type: ignore
            input=symptom_data,
            analysis=symptom_check_obj.analysis,  # type: ignore
            status=symptom_check_obj.status  # type: ignore
        )
        
    except Exception as e:
        logger.error(f"Symptom check error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process symptom check")

@app.get("/symptom-history", response_model=SymptomHistoryResponse)
async def get_symptom_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's symptom check history"""
    try:
        # Fetch symptom checks from database
        stmt = select(SymptomCheck).where(
            SymptomCheck.user_id == current_user.id
        ).order_by(SymptomCheck.created_at.desc())
        
        result = await db.execute(stmt)
        checks = result.scalars().all()
        
        # Convert to response models
        symptom_checks = []
        for check in checks:
            symptom_checks.append(SymptomCheckResponse(
                id=check.id,  # type: ignore
                user_id=check.user_id,  # type: ignore
                timestamp=check.created_at,  # type: ignore
                input=SymptomCheckRequest(
                    age=check.age,  # type: ignore
                    sex=check.sex,  # type: ignore
                    symptoms=check.symptoms,  # type: ignore
                    duration=check.duration,  # type: ignore
                    severity=check.severity,  # type: ignore
                    additional_notes=check.additional_notes  # type: ignore
                ),
                analysis=check.analysis,  # type: ignore
                status=check.status  # type: ignore
            ))
        
        return SymptomHistoryResponse(
            checks=symptom_checks,
            total_count=len(symptom_checks)
        )
        
    except Exception as e:
        logger.error(f"Get symptom history error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve symptom history")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Medical Symptom Checker API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    ) 