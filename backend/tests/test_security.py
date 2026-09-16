"""
Tests for security utilities (password hashing & JWT).
"""
from datetime import timedelta
from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


def test_password_hashing():
    """Test password hashing and verification."""
    password = "DevOpsStrongPassword123!"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword123!", hashed) is False


def test_jwt_token_generation_and_decode():
    """Test JWT creation and payload decoding."""
    user_id = "test-user-uuid-1234"
    token = create_access_token(
        subject=user_id,
        expires_delta=timedelta(minutes=15),
        extra_claims={"role": "STUDENT", "email": "student@cloudforge.io"}
    )
    
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == user_id
    assert payload["role"] == "STUDENT"
    assert payload["email"] == "student@cloudforge.io"
    assert "exp" in payload
    assert "iat" in payload


def test_jwt_token_invalid():
    """Test decoding an invalid token returns None."""
    payload = decode_access_token("invalid.token.string")
    assert payload is None
