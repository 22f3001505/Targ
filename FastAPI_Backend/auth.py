"""
TARG - Authentication System
JWT-based auth with password hashing
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database import get_db
from models_db import User
import os
import re

# ═══════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════
DEFAULT_SECRET_KEY = "targ-secret-key-change-in-production-2024"
SECRET_KEY = os.getenv("SECRET_KEY", DEFAULT_SECRET_KEY)
if SECRET_KEY == DEFAULT_SECRET_KEY and os.getenv("RENDER"):
    raise RuntimeError("SECRET_KEY must be set in production")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
USERNAME_RE = re.compile(r"^[a-zA-Z0-9_][a-zA-Z0-9_.-]{2,31}$")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


# ═══════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════
class SignupRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=32)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(default="", max_length=200)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        value = value.strip().lower()
        if not USERNAME_RE.fullmatch(value):
            raise ValueError("Username must be 3-32 characters and can use letters, numbers, _, ., or -")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if value.strip() != value:
            raise ValueError("Password cannot start or end with spaces")
        if not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
            raise ValueError("Password must include at least one letter and one number")
        return value

    @field_validator("full_name")
    @classmethod
    def clean_full_name(cls, value: str) -> str:
        return " ".join(value.strip().split())

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=1, max_length=128)

    @field_validator("username")
    @classmethod
    def normalize_identifier(cls, value: str) -> str:
        return value.strip().lower()

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60
    user: dict

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str


# ═══════════════════════════════════════════
# PASSWORD UTILS
# ═══════════════════════════════════════════
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ═══════════════════════════════════════════
# JWT TOKEN UTILS
# ═══════════════════════════════════════════
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    if "user_id" in to_encode:
        to_encode.setdefault("sub", str(to_encode["user_id"]))
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc), "typ": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def token_user_id(payload: dict) -> Optional[int]:
    raw_user_id = payload.get("user_id") or payload.get("sub")
    try:
        return int(raw_user_id)
    except (TypeError, ValueError):
        return None


# ═══════════════════════════════════════════
# GET CURRENT USER (Dependency)
# ═══════════════════════════════════════════
def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Optional auth dependency.
    Returns None only when no token was sent; invalid tokens are rejected so
    public endpoints with auto-save cannot silently drop user data.
    """
    if not token:
        return None

    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = token_user_id(payload)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user


def require_auth(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Strict dependency: raises 401 if not authenticated.
    Use this for protected endpoints.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )

    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = token_user_id(payload)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user


# ═══════════════════════════════════════════
# AUTH OPERATIONS
# ═══════════════════════════════════════════
def signup_user(req: SignupRequest, db: Session) -> TokenResponse:
    """Register a new user and return JWT token."""
    email = req.email.strip().lower()
    username = req.username.strip().lower()

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        email=email,
        username=username,
        hashed_password=hash_password(req.password),
        full_name=req.full_name
    )
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email or username already exists")

    token = create_access_token({"user_id": user.id, "username": user.username})

    return TokenResponse(
        access_token=token,
        user={"id": user.id, "email": user.email, "username": user.username, "full_name": user.full_name}
    )


def login_user(req: LoginRequest, db: Session) -> TokenResponse:
    """Authenticate user and return JWT token."""
    identifier = req.username.strip().lower()
    user = db.query(User).filter(
        (User.username == identifier) | (User.email == identifier)
    ).first()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"user_id": user.id, "username": user.username})

    return TokenResponse(
        access_token=token,
        user={"id": user.id, "email": user.email, "username": user.username, "full_name": user.full_name}
    )
