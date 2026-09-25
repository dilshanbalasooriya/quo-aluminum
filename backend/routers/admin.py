from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlmodel import Session, func, select

from fastapi import APIRouter, Depends, HTTPException

from services.security import hash_password, require_admin
from database.connection import DatabaseManager
from database.models import (
    AluminiumProfile,
    CategoryEnum,
    Quotation,
    Setting,
    StatusEnum,
    User,
    WindowDoorType,
)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
)


class RevenueTrendPoint(BaseModel):
    label: str
    value: float


class QuotationStatusItem(BaseModel):
    label: str
    value: int
    color: str


class AdminDashboardStatus(BaseModel):
    daily_sales: float
    monthly_revenue: float
    total_users: int
    active_profiles: int
    revenue_trend: list[RevenueTrendPoint] = []
    quotation_status: list[QuotationStatusItem] = []


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


@router.get("/status", response_model=AdminDashboardStatus)
@router.get("/stats", response_model=AdminDashboardStatus)
def get_dashboard_status(session: Session = Depends(DatabaseManager.get_session)):
    """Return the KPI values and chart summaries for the admin dashboard."""
    now = datetime.now(timezone.utc)
    today_start = datetime.combine(now.date(), datetime.min.time(), tzinfo=timezone.utc)
    month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    next_day = today_start + timedelta(days=1)

    daily_sales = session.exec(
        select(func.coalesce(func.sum(Quotation.total_amount), 0)).where(
            Quotation.created_at >= today_start,
            Quotation.created_at < next_day,
        )
    ).one() or 0

    monthly_revenue = session.exec(
        select(func.coalesce(func.sum(Quotation.total_amount), 0)).where(
            Quotation.created_at >= month_start,
        )
    ).one() or 0

    total_users = session.exec(
        select(func.count(User.id)).where(User.is_deleted == False)  # noqa: E712
    ).one() or 0
    active_profiles = session.exec(
        select(func.count(AluminiumProfile.id)).where(
            AluminiumProfile.is_active.is_(True),
            AluminiumProfile.is_deleted == False,  # noqa: E712
        )
    ).one() or 0

    revenue_trend = []
    for offset in range(6, -1, -1):
        day_value = now.date() - timedelta(days=offset)
        day_start = datetime.combine(day_value, datetime.min.time(), tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)
        day_total = session.exec(
            select(func.coalesce(func.sum(Quotation.total_amount), 0)).where(
                Quotation.created_at >= day_start,
                Quotation.created_at < day_end,
            )
        ).one() or 0
        revenue_trend.append({"label": day_value.strftime("%a"), "value": float(day_total)})

    status_rows = session.exec(
        select(Quotation.status, func.count(Quotation.id)).group_by(Quotation.status)
    ).all()
    status_map = {StatusEnum.DRAFT: 0, StatusEnum.ISSUED: 0}
    for status_value, count in status_rows:
        if status_value in status_map:
            status_map[status_value] = int(count)

    quotation_status = [
        {"label": "Draft", "value": status_map[StatusEnum.DRAFT], "color": "#f59e0b"},
        {"label": "Issued", "value": status_map[StatusEnum.ISSUED], "color": "#10b981"},
    ]

    return {
        "daily_sales": float(daily_sales),
        "monthly_revenue": float(monthly_revenue),
        "total_users": int(total_users),
        "active_profiles": int(active_profiles),
        "revenue_trend": revenue_trend,
        "quotation_status": quotation_status,
    }


@router.patch("/users/{user_id}")
def update_user(
    user_id: int,
    payload: UserUpdate,
    session: Session = Depends(DatabaseManager.get_session),
):
    user = session.get(User, user_id)
    if not user or user.is_deleted:
        raise HTTPException(404, "User not found.")
    if payload.username is not None:
        existing_user = session.exec(
            select(User).where(User.username == payload.username, User.id != user_id)
        ).first()
        if existing_user:
            raise HTTPException(400, "Username already registered.")
        user.username = payload.username
    if payload.email is not None:
        user.email = payload.email
    if payload.password is not None:
        user.password_hash = hash_password(payload.password)
    if payload.is_active is not None:
        user.is_active = payload.is_active
    session.add(user)
    session.commit()
    return {"ok": True}


@router.delete("/users/{user_id}")
def delete_user(user_id: int, session: Session = Depends(DatabaseManager.get_session)):
    user = session.get(User, user_id)
    if not user or user.is_deleted:
        raise HTTPException(404, "User not found.")
    user.is_active = False
    user.is_deleted = True
    suffix = f"__deleted_{user.id}"
    prefix_length = max(1, 50 - len(suffix))
    user.username = f"{user.username[:prefix_length]}{suffix}"
    session.add(user)
    session.commit()
    return {"ok": True}


class ProfileCreate(BaseModel):
    profile_name: str
    brand: Optional[str] = None
    gauge: Decimal
    weight_per_meter: Decimal
    rate_per_kg: Decimal
 
class profileUpdate(BaseModel):
    profile_name: Optional[str] = None
    brand: Optional[str] = None
    gauge: Optional[Decimal] = None
    weight_per_meter: Optional[Decimal] = None
    rate_per_kg: Optional[Decimal] = None
    is_active: Optional[bool] = None
    
    
class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    profile_name: str
    brand: Optional[str] = None
    gauge: Decimal
    weight_per_meter: Decimal
    rate_per_kg: Decimal
    is_active: bool
 

@router.post("/aluminium-profiles", response_model=ProfileOut)
def create_profile(payload: ProfileCreate, session: Session = Depends(DatabaseManager.get_session)):
    profile = AluminiumProfile(**payload.model_dump())
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile
 
 
@router.patch("/aluminium-profiles/{profile_id}", response_model=ProfileOut)
def update_profile(
    profile_id: int,
    payload: profileUpdate,
    session: Session = Depends(DatabaseManager.get_session),
):
    profile = session.get(AluminiumProfile, profile_id)
    if not profile or profile.is_deleted:
        raise HTTPException(404, "Aluminium profile not found.")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(profile, k, v)
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile
 
 
@router.delete("/aluminium-profiles/{profile_id}")
def delete_profile(profile_id: int, session: Session = Depends(DatabaseManager.get_session)):
    """Hide the profile permanently from both admin and worker listings."""
    profile = session.get(AluminiumProfile, profile_id)
    if not profile or profile.is_deleted:
        raise HTTPException(404, "Aluminium profile not found.")
    profile.is_active = False
    profile.is_deleted = True
    session.add(profile)
    session.commit()
    return {"ok": True}





# ============================================================
# Window / Door Types
# ============================================================
 
class TypeCreate(BaseModel):
    type_name: str
    category: CategoryEnum
    vertical_bars_count: int = 2
    horizontal_bars_count: int = 2


class TypeUpdate(BaseModel):
    type_name: Optional[str] = None
    category: Optional[CategoryEnum] = None
    vertical_bars_count: Optional[int] = None
    horizontal_bars_count: Optional[int] = None
    is_active: Optional[bool] = None
 
 
class TypeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    type_name: str
    category: CategoryEnum
    vertical_bars_count: int
    horizontal_bars_count: int
    is_active: bool
 
 
@router.post("/window-door-types", response_model=TypeOut)
def create_type(payload: TypeCreate, session: Session = Depends(DatabaseManager.get_session)):
    obj = WindowDoorType(**payload.model_dump())
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj
 
 
@router.patch("/window-door-types/{type_id}", response_model=TypeOut)
def update_type(
    type_id: int,
    payload: TypeUpdate,
    session: Session = Depends(DatabaseManager.get_session),
):
    obj = session.get(WindowDoorType, type_id)
    if not obj or obj.is_deleted:
        raise HTTPException(404, "Window/door type not found.")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj
 
 
@router.delete("/window-door-types/{type_id}")
def delete_type(type_id: int, session: Session = Depends(DatabaseManager.get_session)):
    obj = session.get(WindowDoorType, type_id)
    if not obj or obj.is_deleted:
        raise HTTPException(404, "Window/door type not found.")
    obj.is_active = False
    obj.is_deleted = True
    session.add(obj)
    session.commit()
    return {"ok": True}
 

