from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.users.schemas import UserDisplaySchema
from app.store.schemas import StoreItemDisplay  # reuse item data


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
# Bar Item
# ----------------------------
class BarItemBase(BaseModel):
    item_id: int
    bar_id: int
    quantity: int
    selling_price: float


class BarItemCreate(BarItemBase):
    pass


class BarItemDisplay(BaseModel):
    id: int
    item_id: int
    bar_id: int
    quantity: int
    selling_price: float
    created_at: datetime
    item: StoreItemDisplay
    bar: BarDisplay

    class Config:
        from_attributes = True


class BarPriceUpdate(BaseModel):
    bar_id: int
    item_id: int
    new_price: float


class BarSaleItemCreate(BaseModel):
    bar_item_id: int
    quantity: int


class BarSaleCreate(BaseModel):
    bar_id: int
    #sold_by_id: int
    items: List[BarSaleItemCreate]


class BarSaleItemDisplay(BaseModel):
    id: int
    quantity: int
    #selling_price: float
    bar_item: BarItemDisplay

    class Config:
        from_attributes = True


class BarSaleDisplay(BaseModel):
    id: int
    bar: BarDisplay
    created_by: str  # ✅ use nested schema here
    sale_date: datetime
    sale_items: List[BarSaleItemDisplay]

    class Config:
        from_attributes = True
