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



class BarStockReceiveCreate(BaseModel):
    bar_id: int
    bar_name: Optional[str]  # <-- Add this
    item_id: int
    item_name: str
    quantity: int
    selling_price: float
    note: Optional[str] = None

class BarInventoryDisplay(BaseModel):
    id: int
    item_id: int
    item_name: Optional[str]
    bar_id: int
    bar_name: Optional[str]  # <-- Add this
    quantity: int
    selling_price: float
    received_at: datetime  # ✅ Include this field
    note: Optional[str]

    class Config:
        orm_mode = True


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

class BarSaleItemSummary(BaseModel):
    item_id: int
    item_name: str  # This must be populated
    quantity: int
    selling_price: float
    total_amount: float

    class Config:
        orm_mode = True


class BarSaleDisplay(BaseModel):
    id: int
    sale_date: datetime
    bar_id: int
    bar_name: str
    created_by: str
    status: str
    total_amount: float
    sale_items: List[BarSaleItemSummary]

    model_config = {
        "from_attributes": True  # replaces orm_mode in Pydantic v2
    }


class BarSaleListResponse(BaseModel):
    total_entries: int
    total_sales_amount: float
    sales: List[BarSaleDisplay]


class BarInventorySummaryDisplay(BaseModel):
    item_id: int
    item_name: str
    quantity: int
    current_unit_price: Optional[float]
    selling_price: Optional[float]

    class Config:
        from_attributes = True

class BarStockUpdate(BaseModel):
    bar_id: int
    item_id: int
    new_quantity: int
    selling_price: Optional[float] = None
    note: Optional[str] = None


class BarStockBalance(BaseModel):
    item_id: int
    item_name: str
    total_issued: int
    total_sold: int
    balance: int
