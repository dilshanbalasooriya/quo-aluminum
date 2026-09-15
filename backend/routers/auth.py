from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlmodel import Session, select

from database.connection import DatabaseManager
from database.models import RoleEnum, User
from services.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
    require_admin
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# --- Schemas ---
class UserRegister(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    role: RoleEnum


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class PasswordReset(BaseModel):
    new_password: str
 

# --- Endpoints ---

@router.post("/register-worker", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_worker(
    user_data: UserRegister,
    session: Session = Depends(DatabaseManager.get_session),
    admin_user:User = Depends(require_admin)
):
    """Registers a new user with the WORKER role."""

    existing_user = session.exec(
        select(User).where(User.username == user_data.username)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    new_worker = User(
        username=user_data.username,
        password_hash=hash_password(user_data.password),
        role=RoleEnum.WORKER,
    )
    session.add(new_worker)
    session.commit()
    session.refresh(new_worker)

    return new_worker

 
@router.get(
    "/users",
    response_model=list[UserResponse],
    dependencies=[Depends(require_admin)],
)
def list_users(session: Session = Depends(DatabaseManager.get_session)):
    """Admin-only: list all logins."""
    return session.exec(select(User)).all()



#Password recovery
router.put(
    "/users/{user_id}/password",
    dependencies=[Depends(require_admin)],
)
def reset_password(
    user_id: int,
    payload: PasswordReset,
    session: Session = Depends(DatabaseManager.get_session),
):
    """Admin-only: set a new password for any user (e.g. a worker who
    forgot theirs). The admin does not need to know the old password."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
    user.password_hash = hash_password(payload.new_password)
    session.add(user)
    session.commit()
    return {"ok": True}

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(DatabaseManager.get_session),
):
    """Authenticates user (Admin or Worker) and returns a JWT access token."""
    user = session.exec(
        select(User).where(User.username == form_data.username)
    ).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value, "user_id": user.id}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns profile information for the authenticated user."""
    return current_user