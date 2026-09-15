from dataclasses import dataclass
from decimal import Decimal

from database.models import AluminiumProfile,WindowDoorType



# ============================================================
# Pricing: frame-only quotation calculation
# ============================================================
"""
    Outer Perimeter (m)     = 2 * (height_m + width_m)
    Extra Internal Bars (m) = (vertical_bars_count * height_m) + (horizontal_bars_count * width_m)
    Total Frame Length (m)  = Outer Perimeter + Extra Internal Bars
 
    Weight (kg) = Total Frame Length (m) * profile.weight_per_meter
    Frame Cost  = Weight (kg) * profile.rate_per_kg
 
    
 
    Item Total = Frame Cost * quantity
 
"""
 
 
@dataclass
class PriceBreakdown:
    frame_length_m: Decimal
    calculated_weight_kg: Decimal
    item_frame_cost: Decimal
    price_per_unit: Decimal
    item_total: Decimal
 
 
def calculate_item_price(
    *,
    height_mm: int,
    width_mm: int,
    quantity: int,
    profile: AluminiumProfile,
    window_door_type: WindowDoorType,
) -> PriceBreakdown:
    if height_mm <= 0 or width_mm <= 0:
        raise ValueError("Height and width must be greater than zero.")
    if quantity <= 0:
        raise ValueError("Quantity must be at least 1.")
 
    height_m = Decimal(height_mm) / Decimal(1000)
    width_m = Decimal(width_mm) / Decimal(1000)
 
    outer_perimeter_m = 2 * (height_m + width_m)
    extra_bars_m = (
        Decimal(window_door_type.vertical_bars_count) * height_m
        + Decimal(window_door_type.horizontal_bars_count) * width_m
    )
    frame_length_m = outer_perimeter_m + extra_bars_m
 
    calculated_weight_kg = frame_length_m * profile.weight_per_meter
    item_frame_cost = calculated_weight_kg * profile.rate_per_kg
 
    
 
    price_per_unit = item_frame_cost
    item_total = price_per_unit * quantity
 
    q = Decimal("0.01")
    return PriceBreakdown(
        frame_length_m=frame_length_m.quantize(Decimal("0.001")),
        calculated_weight_kg=calculated_weight_kg.quantize(Decimal("0.001")),
        item_frame_cost=item_frame_cost.quantize(q),
        price_per_unit=price_per_unit.quantize(q),
        item_total=item_total.quantize(q),
    )
