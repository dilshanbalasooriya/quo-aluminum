from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class RoleEnum(str, Enum):
    ADMIN = "ADMIN"
    WORKER = "WORKER"


class CategoryEnum(str, Enum):
    WINDOW = "WINDOW"
    DOOR = "DOOR"


class StatusEnum(str, Enum):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"


class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, max_length=50)
    password_hash: str = Field(max_length=255)
    role: RoleEnum
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    quotations: List["Quotation"] = Relationship(back_populates="worker")


class AluminiumProfile(SQLModel, table=True):
    __tablename__ = "aluminium_profiles"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    profile_name: str = Field(max_length=100)
    brand: Optional[str] = Field(default=None, max_length=50)
    gauge: Decimal = Field(default=0, max_digits=4, decimal_places=2)
    weight_per_meter: Decimal = Field(default=0, max_digits=10, decimal_places=3)
    rate_per_kg: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WindowDoorType(SQLModel, table=True):
    __tablename__ = "window_door_types"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    type_name: str = Field(max_length=100)
    category: CategoryEnum
    vertical_bars_count: int = Field(default=2)
    horizontal_bars_count: int = Field(default=2)
    hardware_cost: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    glass_rate_per_sqm: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Customer(SQLModel, table=True):
    __tablename__ = "customers"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    phone: str = Field(max_length=20)
    email: Optional[str] = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    quotations: List["Quotation"] = Relationship(back_populates="customer")


class Quotation(SQLModel, table=True):
    __tablename__ = "quotations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    quotation_number: str = Field(unique=True, max_length=50)
    worker_id: int = Field(foreign_key="users.id")
    customer_id: int = Field(foreign_key="customers.id")
    
    worker_fee: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    subtotal: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    total_amount: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    status: StatusEnum = Field(default=StatusEnum.DRAFT)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    worker: User = Relationship(back_populates="quotations")
    customer: Customer = Relationship(back_populates="quotations")
    items: List["QuotationItem"] = Relationship(back_populates="quotation")


class QuotationItem(SQLModel, table=True):
    __tablename__ = "quotation_items"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    quotation_id: int = Field(foreign_key="quotations.id")
    aluminium_profile_id: int = Field(foreign_key="aluminium_profiles.id")
    window_door_type_id: int = Field(foreign_key="window_door_types.id")
    
    width_mm: int
    height_mm: int
    quantity: int = Field(default=1)
    
    calculated_weight_kg: Decimal = Field(default=0, max_digits=10, decimal_places=3)
    item_frame_cost: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    item_hardware_cost: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    item_total: Decimal = Field(default=0, max_digits=10, decimal_places=2)

    # Relationships
    quotation: Quotation = Relationship(back_populates="items")
    # Using forward reference strings or directly passing the class if order allows
    profile: AluminiumProfile = Relationship()
    window_door_type: WindowDoorType = Relationship()