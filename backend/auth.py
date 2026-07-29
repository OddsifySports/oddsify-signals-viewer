"""
Authentication module for Oddsify Signals Viewer
JWT-based authentication with admin/viewer roles
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import jwt, JWTError
from passlib.context import CryptContext
import secrets
import re

# Configuration
JWT_SECRET = secrets.token_urlsafe(32)  # In production, set via environment variable
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Valid membership types
VALID_MEMBERSHIPS = {"TERMINAL", "ONLINE", "INSIDER"}

# Admin email (receives new user credentials)
ADMIN_EMAIL = "admin@oddsifylabs.com"  # Set via environment variable in production


def verify_membership(email: str, membership_type: str) -> bool:
    """
    Verify user has valid Oddsify membership
    
    In production, this would call your membership API or check a database.
    For now, we validate the membership type format.
    
    Args:
        email: User's email address
        membership_type: Must be TERMINAL, ONLINE, or INSIDER
    
    Returns:
        True if membership is valid
    """
    if membership_type.upper() not in VALID_MEMBERSHIPS:
        return False
    
    # Basic email validation
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return False
    
    # TODO: Integrate with actual membership verification system
    # This could be:
    # - Call to Oddsify membership API
    # - Check against whitelist database
    # - Verify payment status
    # - Check Discord/Telegram membership
    
    return True


def generate_username_from_email(email: str) -> str:
    """
    Generate username from email address
    
    Args:
        email: User's email
    
    Returns:
        Username (email local part, sanitized)
    """
    # Extract local part (before @)
    local_part = email.split('@')[0]
    
    # Sanitize: keep only alphanumeric and underscores
    username = re.sub(r'[^a-zA-Z0-9_]', '_', local_part)
    
    # Ensure not empty
    if not username:
        username = "user_" + secrets.token_hex(4)
    
    return username.lower()


def generate_password(length: int = 12) -> str:
    """
    Generate secure random password
    
    Args:
        length: Password length (default 12)
    
    Returns:
        Secure random password
    """
    # Use secrets for cryptographically secure random generation
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    # Ensure password has at least one of each required type
    if not any(c.islower() for c in password):
        password = password[:-1] + secrets.choice("abcdefghijklmnopqrstuvwxyz")
    if not any(c.isupper() for c in password):
        password = password[:-2] + secrets.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + password[-1]
    if not any(c.isdigit() for c in password):
        password = password[:-3] + secrets.choice("0123456789") + password[-2:]
    
    return password


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
    
    Returns:
        True if password matches
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Token payload (should include 'sub' with username)
        expires_delta: Optional custom expiration time
    
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict]:
    """
    Decode and validate JWT access token
    
    Args:
        token: JWT token string
    
    Returns:
        Token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def get_user_from_token(token: str) -> Optional[Dict]:
    """
    Extract user information from token
    
    Args:
        token: JWT token
    
    Returns:
        User info dict with username, role, etc.
    """
    payload = decode_access_token(token)
    
    if not payload:
        return None
    
    username = payload.get("sub")
    role = payload.get("role")
    
    if not username or not role:
        return None
    
    return {
        "username": username,
        "role": role,
        "email": payload.get("email"),
        "membership": payload.get("membership")
    }


def format_admin_notification(email: str, username: str, password: str, membership: str) -> str:
    """
    Format admin notification email for new user
    
    Args:
        email: User's email
        username: Generated username
        password: Generated password
        membership: Membership type
    
    Returns:
        Formatted notification message
    """
    return f"""
NEW USER REGISTRATION - Oddsify Signals Viewer
=============================================

Email: {email}
Username: {username}
Password: {password}
Membership: {membership}
Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

ACTION REQUIRED:
- Verify user's membership status
- If valid, credentials are ready for use
- If invalid, deactivate user account

Login URL: https://oddsify-signals-viewer-production.up.railway.app

---
Oddsify Signals Viewer - Auto-generated notification
"""


# Test function
if __name__ == "__main__":
    # Test username generation
    test_email = "john.doe@example.com"
    username = generate_username_from_email(test_email)
    print(f"Email: {test_email} → Username: {username}")
    
    # Test password generation
    password = generate_password()
    print(f"Generated password: {password}")
    
    # Test password hashing
    hashed = hash_password(password)
    print(f"Hashed: {hashed[:20]}...")
    print(f"Verify: {verify_password(password, hashed)}")
    
    # Test token creation
    token_data = {
        "sub": username,
        "role": "viewer",
        "email": test_email,
        "membership": "TERMINAL"
    }
    token = create_access_token(token_data)
    print(f"Token: {token[:50]}...")
    
    # Test token decoding
    user = get_user_from_token(token)
    print(f"Decoded user: {user}")
