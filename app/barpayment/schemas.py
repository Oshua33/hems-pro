# app/barpayment/schemas.py

from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime
from typing import Optional


class BarPaymentCreate(BaseModel):
    bar_sale_id: int
    amount: float
    method: Literal["cash", "transfer", "pos"]
    note: Optional[str] = None

class BarPaymentDisplay(BaseModel):
    id: int
    bar_sale_id: int
    amount: float
    method: str
    note: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True



class BarPaymentUpdate(BaseModel):
    amount: Optional[float] = None
    payment_method: Optional[str] = None

class BarPaymentVoid(BaseModel):
    void: bool  # If True, will void


