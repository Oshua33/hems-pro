from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.store.schemas import StoreItemDisplay
from app.users.schemas import UserDisplaySchema


# ----------------------------
# Bar
# ----------------------------
class BarBase(BaseModel):
    name: str
    location: Optional[str] = None


class BarCreate(BarBase):
    pass


class BarDisplay(BarBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ----------------------------
# Bar Inventory (item + selling price)
# ----------------------------
class BarInventoryBase(BaseModel):
    bar_id: int
    item_id: int


class BarInventoryCreate(BarInventoryBase):
    selling_price: float


class BarInventoryUpdatePrice(BaseModel):
    selling_price: float

class BarPriceUpdate(BaseModel):
    bar_id: int
    item_id: int
    new_price: float



class BarInventoryDisplay(BaseModel):
    id: int
    bar_id: int
    item_id: int
    quantity: int
    selling_price: float
    item: StoreItemDisplay
    bar: BarDisplay

    class Config:
        from_attributes = True


# ----------------------------
# Bar Sale
# ----------------------------
class BarSaleItemCreate(BaseModel):
    item_id: int
    quantity: int



class BarSaleCreate(BaseModel):
    bar_id: int
    items: List[BarSaleItemCreate]


class BarSaleItemDisplay(BaseModel):
    id: int
    quantity: int
    total_amount: float
    bar_inventory: BarInventoryDisplay

    class Config:
        from_attributes = True


class BarSaleDisplay(BaseModel):
    id: int
    bar: BarDisplay
    created_by: str  # Only username
    sale_date: datetime
    sale_items: List[BarSaleItemDisplay]

    class Config:
        from_attributes = True


class BarInventorySummaryDisplay(BaseModel):
    item_id: int
    item_name: str
    quantity: int
    current_unit_price: Optional[float]
    selling_price: Optional[float]

    class Config:
        from_attributes = True

