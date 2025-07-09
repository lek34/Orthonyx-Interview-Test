from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Index, BigInteger
from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy.orm import relationship
from .database import Base as SQLAlchemyBase


# PYDANTIC MODELS (API Request/Response)


class UserSignup(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password (min 6 characters)")

class UserSignin(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")

class UserResponse(BaseModel):
    id: int
    email: str
    api_key: str
    created_at: datetime

    class Config:
        from_attributes = True

class SymptomCheckRequest(BaseModel):
    age: int = Field(..., ge=0, le=120, description="Patient age")
    sex: str = Field(..., description="Patient sex (male/female/other)")
    symptoms: str = Field(..., min_length=10, description="Description of symptoms")
    duration: str = Field(..., description="Duration of symptoms")
    severity: int = Field(..., ge=1, le=10, description="Symptom severity (1-10)")
    additional_notes: Optional[str] = Field(None, description="Additional notes")

class SymptomCheckResponse(BaseModel):
    id: int
    user_id: int
    timestamp: datetime
    input: SymptomCheckRequest
    analysis: str
    status: str

    class Config:
        from_attributes = True

class SymptomHistoryResponse(BaseModel):
    checks: List[SymptomCheckResponse]
    total_count: int

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None

class APIKeyHeader(BaseModel):
    api_key: str = Field(..., description="API key for authentication")


# SQLALCHEMY MODELS (Database Tables)

class User(SQLAlchemyBase):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(VARCHAR(255), unique=True, nullable=False, index=True)
    password_hash = Column(VARCHAR(255), nullable=False)
    api_key = Column(VARCHAR(64), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    symptom_checks = relationship("SymptomCheck", back_populates="user", cascade="all, delete-orphan")

class SymptomCheck(SQLAlchemyBase):
    __tablename__ = "symptom_checks"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    age = Column(Integer, nullable=False)
    sex = Column(VARCHAR(10), nullable=False)
    symptoms = Column(Text, nullable=False)
    duration = Column(VARCHAR(100), nullable=False)
    severity = Column(Integer, nullable=False)
    additional_notes = Column(Text, nullable=True)
    analysis = Column(Text, nullable=False)
    status = Column(VARCHAR(20), default="completed")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="symptom_checks")

    # Indexes
    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),
    ) 