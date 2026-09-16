"""
Security Module - Password Hashing and JWT Token Management.

Why this exists:
1. Passlib Bcrypt:
   Provides adaptive, salted cryptographic one-way hashing for user passwords.
   Never logs or stores plaintext passwords.

2. PyJWT Token Generation & Verification:
   Produces cryptographically signed JWT access tokens (short-lived) and refresh tokens (long-lived).

3. SHA-256 Token Hashing:
   Hashes refresh tokens prior to database storage, ensuring that even if database read access
   is compromised, raw refresh tokens cannot be used to forge authenticated sessions.
"""
from datetime import datetime, timedelta, timezone
import hashlib
from typing import Any, Dict, Optional, Tuple, Union
import uuid
import jwt
from passlib.context import CryptContext
from app.core.config import settings

# CryptContext configured with bcrypt scheme
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its bcrypt hashed digest."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a bcrypt password hash."""
    return pwd_context.hash(password)


def hash_token(token: str) -> str:
    """Compute SHA-256 hash of a token for secure database indexing."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_access_token(
    subject: Union[str, Any],
    role: str = "student",
    email: Optional[str] = None,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate an encoded JWT access token with subject, role, and expiration claims.
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "email": email,
        "role": role,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    
    if extra_claims:
        to_encode.update(extra_claims)

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> Tuple[str, datetime]:
    """
    Generate an encoded JWT refresh token and return (raw_token, expiration_datetime).
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    jti = str(uuid.uuid4())
    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "jti": jti,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    raw_token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return raw_token, expire


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate any JWT token (access or refresh).
    Returns decoded claims dictionary if valid, or None if expired/malformed.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.PyJWTError:
        return None


# Backward-compatible alias
decode_access_token = decode_token
