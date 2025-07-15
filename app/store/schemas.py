from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ----------------------------
# Store Category
# ----------------------------
class StoreCategoryBase(BaseModel):
    name: str


class StoreCategoryCreate(StoreCategoryBase):
    pass


class StoreCategoryDisplay(StoreCategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ----------------------------
# Store Item
# ----------------------------
class StoreItemBase(BaseModel):
    name: str
    unit: str
    category_id: Optional[int] = None


class StoreItemCreate(StoreItemBase):
    pass


class StoreItemDisplay(BaseModel):
    id: int
    name: str
    unit: str
    category: Optional[StoreCategoryDisplay]
    created_at: datetime


    class Config:
        from_attributes = True


# ----------------------------
# Store Stock Entry (Purchase)
# ----------------------------
class StoreStockEntryCreate(BaseModel):
    item_id: int
    quantity: int
    unit_price: Optional[float] = None
    vendor: Optional[str] = None


class StoreStockEntryDisplay(BaseModel):
    id: int
    item: StoreItemDisplay
    quantity: int
    unit_price: Optional[float]
    total_amount: Optional[float]  # ✅ new
    vendor: Optional[str]
    purchase_date: datetime

    class Config:
        from_attributes = True


# ----------------------------
# Store Issue
# ----------------------------
class IssueItemCreate(BaseModel):  # ✅ renamed from StoreIssueItemBase
    item_id: int
    quantity: int


class IssueCreate(BaseModel):  # ✅ renamed from StoreIssueCreate
    issue_to: str            # "bar" or "restaurant"
    issued_to_id: int        # ID of the bar/restaurant
    issue_items: List[IssueItemCreate]  # ✅ renamed from 'items'
    issue_date: datetime = Field(default_factory=datetime.utcnow)



class IssueItemDisplay(BaseModel):  # ✅ renamed from StoreIssueItemDisplay
    id: int
    item: StoreItemDisplay
    quantity: int

    class Config:
        from_attributes = True


class IssueDisplay(BaseModel):  # ✅ renamed from StoreIssueDisplay
    id: int
    issue_to: str
    issued_to_id: int
    issue_date: datetime
    issue_items: List[IssueItemDisplay]

    class Config:
        from_attributes = True
