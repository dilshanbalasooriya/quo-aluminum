"""
Read-only routes any logged-in user can call (worker or admin) -- workers
need these to look up rates and types while building a quotation. All
writes to this data live in routers/admin.py instead.
"""

from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlmodel import Session, select

from database.connection import DatabaseManager
from database.models import AluminiumProfile, WindowDoorType, CategoryEnum, Setting
from services.security import get_current_user

router = APIRouter(prefix="/catalog", tags=["Catalog"], dependencies=[Depends(get_current_user)])


class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    profile_name: str
    brand: Optional[str] = None
    gauge: Decimal
    weight_per_meter: Decimal
    rate_per_kg: Decimal
    is_active: bool


class TypeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    type_name: str
    category: CategoryEnum
    vertical_bars_count: int
    horizontal_bars_count: int
    is_active: bool


class SettingOut(BaseModel):
    key: str
    value: str


@router.get("/aluminium-profiles", response_model=list[ProfileOut])
def list_profiles(
    include_inactive: bool = False,
    session: Session = Depends(DatabaseManager.get_session),
):
    stmt = select(AluminiumProfile)
    if not include_inactive:
        stmt = stmt.where(AluminiumProfile.is_active == True)  # noqa: E712
    return session.exec(stmt).all()


@router.get("/window-door-types", response_model=list[TypeOut])
def list_types(
    include_inactive: bool = False,
    session: Session = Depends(DatabaseManager.get_session),
):
    stmt = select(WindowDoorType)
    if not include_inactive:
        stmt = stmt.where(WindowDoorType.is_active == True)  # noqa: E712
    return session.exec(stmt).all()


@router.get("/settings/{key}", response_model=SettingOut)
def read_setting(key: str, session: Session = Depends(DatabaseManager.get_session)):
    row = session.get(Setting, key)
    return SettingOut(key=key, value=row.value if row else "0")