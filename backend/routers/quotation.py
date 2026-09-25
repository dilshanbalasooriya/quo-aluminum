from zoneinfo import ZoneInfo
from datetime import datetime
from decimal import Decimal
from typing import List, Optional


from fastapi import APIRouter, Depends, HTTPException,Response
from pydantic import BaseModel, ConfigDict
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from database.connection import DatabaseManager
from database.models import (
    AluminiumProfile,
    Customer,
    Quotation,
    QuotationItem,
    Setting,
    StatusEnum,
    User,
    WindowDoorType,
)
from configs.config import(
    COMPANY_ADDRESS,
    COMPANY_LOGO_URL,
    COMPANY_NAME,
    COMPANY_PHONE,
    COMPANY_WEBSITE,
)
from services.calulate_service import PriceBreakdown, calculate_item_price
from services.security import get_current_user

import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader




router = APIRouter(prefix="/quotations", tags=["Quotations"], dependencies=[Depends(get_current_user)])
templates_dir = Path(__file__).parent.parent / "templates"
jinja_env = Environment(loader=FileSystemLoader(str(templates_dir)))



# --- Schemas ---

class PricePreviewRequest(BaseModel):
    aluminium_profile_id: int
    window_door_type_id: int
    height_mm: int
    width_mm: int
    quantity: int = 1


class PricePreviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    frame_length_m: float
    calculated_weight_kg: float
    item_frame_cost: float
    price_per_unit: float
    item_total: float


class QuotationItemCreate(BaseModel):
    aluminium_profile_id: int
    window_door_type_id: int
    height_mm: int
    width_mm: int
    quantity: int = 1


class CreateQuotationRequest(BaseModel):
    customer_name: str
    customer_phone: Optional[str] = ""
    worker_fee: Optional[float] = 0.0
    items: List[QuotationItemCreate]
    


class QuotationItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    aluminium_profile_id: int
    window_door_type_id: int
    width_mm: int
    height_mm: int
    quantity: int
    calculated_weight_kg: float
    item_frame_cost: float
    item_total: float


class QuotationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    quotation_number: str
    customer_name: str
    worker_fee: float
    subtotal: float
    total_amount: float
    status: StatusEnum
    created_at: datetime
    items: List[QuotationItemResponse]



def _generate_quotation_number(session: Session) -> str:
    today = datetime.now(ZoneInfo("Asia/Colombo")).strftime("%Y%m%d")
    prefix = f"QT-{today}-"
    last = session.exec(
        select(Quotation.quotation_number)
        .where(Quotation.quotation_number.startswith(prefix))
        .order_by(Quotation.quotation_number.desc())
    ).first()
    next_seq = int(last.rsplit("-", 1)[1]) + 1 if last else 1
    return f"{prefix}{next_seq:04d}"
# --- Routes ---

@router.post("/price-preview", response_model=PricePreviewResponse)
def price_preview(
    payload: PricePreviewRequest,
    session: Session = Depends(DatabaseManager.get_session),
):
    """Stateless calculation -- nothing is saved."""
    profile = session.get(AluminiumProfile, payload.aluminium_profile_id)
    if not profile or not profile.is_active or profile.is_deleted:
        raise HTTPException(404, "Aluminium profile not found or inactive.")

    window_door_type = session.get(WindowDoorType, payload.window_door_type_id)
    if not window_door_type or not window_door_type.is_active or window_door_type.is_deleted:
        raise HTTPException(404, "Window/door type not found or inactive.")

    try:
        breakdown: PriceBreakdown = calculate_item_price(
            height_mm=payload.height_mm,
            width_mm=payload.width_mm,
            quantity=payload.quantity,
            profile=profile,
            window_door_type=window_door_type,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))

    return PricePreviewResponse(
        frame_length_m=float(breakdown.frame_length_m),
        calculated_weight_kg=float(breakdown.calculated_weight_kg),
        item_frame_cost=float(breakdown.item_frame_cost),
        price_per_unit=float(breakdown.price_per_unit),
        item_total=float(breakdown.item_total),
    )


@router.get("")
def list_quotations(
    session: Session = Depends(DatabaseManager.get_session),
    current_user: User = Depends(get_current_user),
):
    rows = session.exec(
        select(Quotation, Customer)
        .join(Customer, Customer.id == Quotation.customer_id)
        .order_by(Quotation.id.desc())
    ).all()
    return [
        {
            "id": q.id,
            "quotation_number": q.quotation_number,
            "customer_name": c.name,
            "customer_phone": c.phone,
            "subtotal": q.subtotal,
            "worker_fee": q.worker_fee,
            "total": q.subtotal + q.worker_fee,
            "created_at": q.created_at,
        }
        for q, c in rows
    ]

@router.post("", response_model=QuotationResponse)
def create_quotation(
    payload: CreateQuotationRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(DatabaseManager.get_session),
):
    if not payload.items:
        raise HTTPException(400, "At least one item is required to create a quotation.")

# Fee need to get from the worker. worker can deside the working fee.
    # 1. Fetch worker fee from settings table
      
    if payload.worker_fee is not None:
        worker_fee = Decimal(str(payload.worker_fee))
    else:
        fee_setting = session.get(Setting, "default_worker_fee")
        if not fee_setting:
            raise HTTPException(500, "Default worker fee is not configured.")
        worker_fee = Decimal(fee_setting.value)

    if worker_fee < 0:
        raise HTTPException(400, "Worker fee cannot be negative.")
    
    # 2. Create simplified Customer record
    customer = Customer(
        name=payload.customer_name,
        phone=payload.customer_phone or ""
    )
    session.add(customer)
    session.flush()  # Populates customer.id

    # 3. Process each quotation item
    subtotal = Decimal("0.00")
    quotation_items: List[QuotationItem] = []

    for item_data in payload.items:
        profile = session.get(AluminiumProfile, item_data.aluminium_profile_id)
        if not profile or not profile.is_active or profile.is_deleted:
            raise HTTPException(404, f"Profile ID {item_data.aluminium_profile_id} not found or inactive.")

        window_door_type = session.get(WindowDoorType, item_data.window_door_type_id)
        if not window_door_type or not window_door_type.is_active or window_door_type.is_deleted:
            raise HTTPException(404, f"Window/Door Type ID {item_data.window_door_type_id} not found or inactive.")

        try:
            breakdown = calculate_item_price(
                height_mm=item_data.height_mm,
                width_mm=item_data.width_mm,
                quantity=item_data.quantity,
                profile=profile,
                window_door_type=window_door_type,
            )
        except ValueError as e:
            raise HTTPException(400, str(e))

        subtotal += breakdown.item_total

        quotation_item = QuotationItem(
            aluminium_profile_id=profile.id,
            window_door_type_id=window_door_type.id,
            width_mm=item_data.width_mm,
            height_mm=item_data.height_mm,
            quantity=item_data.quantity,
            calculated_weight_kg=breakdown.calculated_weight_kg,
            item_frame_cost=breakdown.item_frame_cost,
            item_total=breakdown.item_total,
        )
        quotation_items.append(quotation_item)

    # 4. Save main Quotation record
    total_amount = subtotal + worker_fee
    quotation = Quotation(
        quotation_number=_generate_quotation_number(session),
        worker_id=current_user.id,
        customer_id=customer.id,
        worker_fee=worker_fee,
        subtotal=subtotal,
        total_amount=total_amount,
        status=StatusEnum.ISSUED,
        items=quotation_items,
    )
    session.add(quotation)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Another quotation was issued at the same moment. Please try again.")
    session.refresh(quotation)

    return QuotationResponse(
        id=quotation.id,
        quotation_number=quotation.quotation_number,
        customer_name=customer.name,
        worker_fee=float(quotation.worker_fee),
        subtotal=float(quotation.subtotal),
        total_amount=float(quotation.total_amount),
        status=quotation.status,
        created_at=quotation.created_at,
        items=[
            QuotationItemResponse(
                id=item.id,
                aluminium_profile_id=item.aluminium_profile_id,
                window_door_type_id=item.window_door_type_id,
                width_mm=item.width_mm,
                height_mm=item.height_mm,
                quantity=item.quantity,
                calculated_weight_kg=float(item.calculated_weight_kg),
                item_frame_cost=float(item.item_frame_cost),
                item_total=float(item.item_total),
            )
            for item in quotation.items
        ],
    )


@router.get("/quot-pdf/{quotation_id}/invoice.pdf")
def generate_quotation_pdf(
    quotation_id: int,
    session: Session = Depends(DatabaseManager.get_session),
    current_user: User = Depends(get_current_user),
):
    # 1. Fetch Quotation record
    quotation = session.get(Quotation, quotation_id)
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")

    customer = session.get(Customer, quotation.customer_id)

    # 2. Compute Worker Fee Percentage dynamically
    worker_fee_pct = 0.0
    if quotation.subtotal > 0:
        worker_fee_pct = round(float((quotation.worker_fee / quotation.subtotal) * 100), 2)

    # 3. Read Company settings from Environment variables
    company_context = {
        "company_name":COMPANY_NAME,
        "company_address": COMPANY_ADDRESS,
        "company_phone": COMPANY_PHONE,
        "company_website": COMPANY_WEBSITE,
        "company_logo":COMPANY_LOGO_URL 
    }
    # 4. Render HTML template
    template = jinja_env.get_template("quotation.html")
    rendered_html = template.render(
        quotation=quotation,
        customer=customer,
        items=quotation.items,
        worker_fee_pct=worker_fee_pct,
        **company_context,
    )

    # 5. Generate PDF with xhtml2pdf
    from xhtml2pdf import pisa
    from io import BytesIO
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(
        rendered_html, dest=pdf_buffer
    )
    if pisa_status.err:
        raise HTTPException(status_code=500, detail="PDF generation failed")
    pdf_bytes = pdf_buffer.getvalue()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename=Quotation_{quotation.quotation_number}.pdf"
        },
    )


