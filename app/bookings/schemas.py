#CheckInSchema
from pydantic import BaseModel, root_validator
from typing import Optional, Literal
from datetime import date
from pydantic import BaseModel, validator
from datetime import datetime, timezone


class BookingSchema(BaseModel):
    room_number: str
    guest_name: str
    gender: Literal["Male", "Female"]
    mode_of_identification: Literal["National Id Card", "Voter Card", "Id Card", "Passport"]
    identification_number: Optional[str] = None
    address: str
    arrival_date: date
    departure_date: date
    booking_type: Literal["checked-in", "reservation", "complimentary"]
    phone_number: str
    number_of_days: Optional[int] = None
    created_by: Optional[str] = None
    vehicle_no: Optional[str] = None  # ✅ NEW FIELD
    attachment: Optional[str] = None  # ✅ NEW FIELD (should be a file path or URL)

    class Config:
        from_attributes = True

    @root_validator(pre=True)
    def calculate_number_of_days(cls, values):
        arrival_date = values.get("arrival_date")
        departure_date = values.get("departure_date")
        if isinstance(arrival_date, str):
            arrival_date = datetime.strptime(arrival_date, "%Y-%m-%d").date()
            values["arrival_date"] = arrival_date
        if isinstance(departure_date, str):
            departure_date = datetime.strptime(departure_date, "%Y-%m-%d").date()
            values["departure_date"] = departure_date
        if arrival_date and departure_date:
            values["number_of_days"] = (departure_date - arrival_date).days
        return values


class BookingSchemaResponse(BaseModel):
    id: int
    room_number: str
    guest_name: str
    gender: Literal["Male", "Female"]
    mode_of_identification: Literal["National Id Card", "Voter Card", "Id Card", "Passport"]
    identification_number: Optional[str]
    address: str
    arrival_date: date
    departure_date: date
    booking_type: Literal["checked-in", "reservation", "complimentary"]
    phone_number: str
    status: Optional[str] = "reserved"
    payment_status: Optional[str] = "pending"
    number_of_days: Optional[int] = None  # ✅ supported and computed
    booking_cost: Optional[float] = None
    is_checked_out: Optional[bool] = False
    cancellation_reason: Optional[str] = None
    created_by: str
    vehicle_no: Optional[str] = None  # ✅ NEW FIELD
    attachment: Optional[str] = None  # ✅ NEW FIELD

    class Config:
        from_attributes = True


class UserDisplaySchema(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True
        

class CheckInUpdateSchema(BaseModel):
    room_number: str
    guest_name: str
    arrival_date: Optional[date]
    departure_date: Optional[date]
    phone_number: str