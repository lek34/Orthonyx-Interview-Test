import secrets
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import UserSignup, UserSignin, UserResponse, User

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def generate_api_key() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    async def create_user(user_data: UserSignup, db: AsyncSession) -> UserResponse:
        # Check if user already exists
        stmt = select(User).where(User.email == user_data.email)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise ValueError("User with this email already exists")

        # Generate API key
        api_key = AuthService.generate_api_key()
        password_hash = AuthService.hash_password(user_data.password)

        # Create new user
        new_user = User(
            email=user_data.email,
            password_hash=password_hash,
            api_key=api_key
        )

        # Add to database
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return UserResponse(
            id=new_user.id,  # type: ignore
            email=new_user.email,  # type: ignore
            api_key=new_user.api_key,  # type: ignore
            created_at=new_user.created_at  # type: ignore
        )

    @staticmethod
    async def authenticate_user(user_data: UserSignin, db: AsyncSession) -> UserResponse:
        # Find user by email
        stmt = select(User).where(User.email == user_data.email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError("Invalid email or password")

        # Verify password
        if not AuthService.verify_password(user_data.password, user.password_hash):  # type: ignore
            raise ValueError("Invalid email or password")

        return UserResponse(
            id=user.id,  # type: ignore
            email=user.email,  # type: ignore
            api_key=user.api_key,  # type: ignore
            created_at=user.created_at  # type: ignore
        )

    @staticmethod
    async def get_user_by_api_key(api_key: str, db: AsyncSession):
        stmt = select(User).where(User.api_key == api_key)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

# Create auth service instance
auth_service = AuthService() 