
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr
from pwdlib import PasswordHash

from database.connection import get_database
from database.user_repository import create_user, get_user_by_email


auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
password_hash = PasswordHash.recommended()
bearer_scheme = HTTPBearer(auto_error=False)

SESSION_COLLECTION = "sessions"
NORMAL_SESSION_HOURS = 12
REMEMBER_ME_DAYS = 30


class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    confirm_password: str
    terms_accepted: bool


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False


def hash_token(token: str) -> str:
    """Hash a session token before storing or looking it up."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def public_user(user: dict) -> dict:
    """Return safe user fields required by the frontend."""
    return {
        "user_id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
    }


@auth_router.post("/register")
async def register(request: RegisterRequest):
    if not request.terms_accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Terms and conditions must be accepted.",
        )

    if request.password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match.",
        )

    existing_user = await get_user_by_email(request.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    hashed_password = password_hash.hash(request.password)

    user = await create_user(
        name=request.full_name.strip(),
        email=request.email,
        password_hash=hashed_password,
    )

    return {
        "message": "Registration successful",
        "user": public_user(user),
    }


@auth_router.post("/login")
async def login(request: LoginRequest):
    user = await get_user_by_email(request.email)

    if not user or not password_hash.verify(
        request.password,
        user["password_hash"],
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )

    now = datetime.now(timezone.utc)

    if request.remember_me:
        expires_at = now + timedelta(days=REMEMBER_ME_DAYS)
    else:
        expires_at = now + timedelta(hours=NORMAL_SESSION_HOURS)

    token = secrets.token_urlsafe(32)
    db = get_database()

    await db[SESSION_COLLECTION].insert_one(
        {
            "token_hash": hash_token(token),
            "email": user["email"],
            "created_at": now,
            "expires_at": expires_at,
        }
    )

    return {
        "message": "Login successful",
        "token": token,
        "user": public_user(user),
    }


@auth_router.get("/me")
async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
):
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    now = datetime.now(timezone.utc)
    db = get_database()

    session = await db[SESSION_COLLECTION].find_one(
        {
            "token_hash": hash_token(credentials.credentials),
            "expires_at": {"$gt": now},
        }
    )

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await get_user_by_email(session["email"])

    if not user or not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is unavailable.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return public_user(user)
