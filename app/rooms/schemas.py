from pydantic import BaseModel
from typing import List
from datetime import datetime
from typing import Optional
from typing import Literal
from decimal import Decimal
from datetime import date

        

class RoomSchema(BaseModel):
    room_number: str
    room_type: str
    amount: float
    status: Literal["available", "maintenance"]  # Limited to booking-safe statuses

    class Config:
        from_attributes = True



class RoomFaultSchema(BaseModel):
    id: Optional[int] = None  # ✅ Add this to allow updating existing faults
    room_number: str
    description: str
    resolved: bool = False

    class Config:
        from_attributes = True
        

class RoomList(BaseModel):
    room_number: str
    room_type: str
    amount: float
    

    class Config:
        from_attributes = True
        
        
class RoomUpdateSchema(BaseModel):
    room_number: Optional[str] = None
    room_type: Optional[str] = None
    amount: Optional[int] = None
    status: Optional[Literal["available", "maintenance"]] = None
    faults: Optional[List[RoomFaultSchema]] = None  # ✅ Accept faults with optional IDs

    class Config:
        from_attributes = True



class RoomFaultOut(BaseModel):
    id: int
    room_number: str
    description: str
    resolved: bool
    created_at: date
    resolved_at: Optional[date] = None

    class Config:
        from_attributes = True



class FaultUpdate(BaseModel):
    id: int
    resolved: bool

