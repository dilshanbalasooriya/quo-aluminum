from sqlmodel import Session
from pydantic import BaseModel,ConfigDict
from typing import Optional
from decimal import Decimal


from fastapi import APIRouter,Depends,HTTPException

from services.security import require_admin
from database.connection import DatabaseManager
from database.models import AluminiumProfile, WindowDoorType, CategoryEnum, Setting

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies= [Depends(require_admin)]
    )


class ProfileCreate(BaseModel):
    profile_name: str
    brand: Optional[str] = None
    gauge: Decimal
    weight_per_meter: Decimal
    rate_per_kg: Decimal
 
 
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
    payload: ProfileCreate,
    session: Session = Depends(DatabaseManager.get_session),
):
    profile = session.get(AluminiumProfile, profile_id)
    if not profile:
        raise HTTPException(404, "Aluminium profile not found.")
    for k, v in payload.model_dump().items():
        setattr(profile, k, v)
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile
 
 
@router.delete("/aluminium-profiles/{profile_id}")
def deactivate_profile(profile_id: int, session: Session = Depends(DatabaseManager.get_session)):
    """Soft delete -- keeps past quotations that reference this profile intact."""
    profile = session.get(AluminiumProfile, profile_id)
    if not profile:
        raise HTTPException(404, "Aluminium profile not found.")
    profile.is_active = False
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
    payload: TypeCreate,
    session: Session = Depends(DatabaseManager.get_session),
):
    obj = session.get(WindowDoorType, type_id)
    if not obj:
        raise HTTPException(404, "Window/door type not found.")
    for k, v in payload.model_dump().items():
        setattr(obj, k, v)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj
 
 
@router.delete("/window-door-types/{type_id}")
def deactivate_type(type_id: int, session: Session = Depends(DatabaseManager.get_session)):
    obj = session.get(WindowDoorType, type_id)
    if not obj:
        raise HTTPException(404, "Window/door type not found.")
    obj.is_active = False
    session.add(obj)
    session.commit()
    return {"ok": True}
 

