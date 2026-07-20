import time
import jwt
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token
)

def test_password_hashing():
    """
    Test that plaintext passwords are correctly hashed and that hashes differ from plaintext.
    """
    raw_pass = "mypassword123"
    hashed = hash_password(raw_pass)
    
    assert hashed != raw_pass
    assert hashed.startswith("$2b$")  # Bcrypt marker

def test_password_verification():
    """
    Test password verification works correctly for correct passwords and rejects incorrect ones.
    """
    raw_pass = "mypassword123"
    hashed = hash_password(raw_pass)
    
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("wrongpassword", hashed) is False
    assert verify_password("", hashed) is False

def test_jwt_token_generation_and_decoding():
    """
    Test access token generation and successful decoding of the subject.
    """
    username = "testuser"
    token = create_access_token(username)
    
    assert isinstance(token, str)
    assert len(token) > 0
    
    decoded_user = verify_access_token(token)
    assert decoded_user == username

def test_jwt_token_validation_failures():
    """
    Test decoding behaves correctly for invalid or malformed tokens.
    """
    assert verify_access_token("malformed.token.here") is None
    assert verify_access_token("") is None
