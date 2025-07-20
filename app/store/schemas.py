from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.vendor.schemas import VendorDisplay  # ✅ import this
from app.vendor.schemas import VendorInStoreDisplay  # make sure this import path is correct


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
    item_name: str
    quantity: int
    unit_price: Optional[float] = None
    vendor_id: Optional[int] = None  # 🔗 vendor ID
    purchase_date: datetime = Field(default_factory=datetime.utcnow)
    #created_by: Optional[str] = None

class PurchaseCreateList(BaseModel):
    id: int
    item_id: int
    item_name: str
    quantity: int
    unit_price: float
    total_amount: float
    vendor_id: Optional[int] = None  # 🔗 vendor ID
    purchase_date: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None


class StoreStockEntryDisplay(BaseModel):
    id: int
    item_name: str
    quantity: int
    unit_price: float
    total_amount: float
    vendor_name: Optional[str]
    purchase_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime
    created_by: Optional[str]

    class Config:
        orm_mode = True

class UpdatePurchase(BaseModel):
    id: int
    item_name: str
    quantity: int
    unit_price: float
    total_amount: float
    vendor_id: int
    purchase_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime
    created_by: Optional[str]

    class Config:
        orm_mode = True



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


