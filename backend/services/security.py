import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from pwdlib import PasswordHash

from database.connection import DatabaseManager
from database.models import RoleEnum, User
from configs.config import SECRET_KEY
# JWT Settings
SECRET_KEY = SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 Hours

# Use pwdlib's recommended settings (Defaults to Argon2id)
password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# --- Password Utilities ---
def hash_password(password: str) -> str:
    """Hashes a password using Argon2id"""
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the hashed version"""
    return password_hash.verify(plain_password, hashed_password)


# --- JWT Utilities ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# --- Authentication Dependencies ---
def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(DatabaseManager.get_session),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user