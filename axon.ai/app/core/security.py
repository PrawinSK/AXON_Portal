import datetime
import bcrypt
import jwt
from typing import Optional

# Secret key for JWT signing (kept in config or secure default for dev)
JWT_SECRET_KEY = "axon-secret-key-super-secure-production-ready-2026"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


def hash_password(password: str) -> str:
    """Hashes a plaintext password using bcrypt with salt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def create_access_token(
    user_id: str,
    role: str,
    department: str,
    name: str,
    roll_number: Optional[str] = None
) -> str:
    """
    Issues a signed JWT containing sub, role, department, and expiration.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "sub": user_id,
        "role": role,
        "department": department,
        "name": name,
        "roll_number": roll_number,
        "iat": now,
        "exp": now + datetime.timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decodes and verifies a JWT token.
    Raises jwt.PyJWTError if expired or invalid.
    """
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
