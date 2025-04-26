from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

import pytz
from sqlalchemy.sql import func

def get_local_time():
    lagos_tz = pytz.timezone("Africa/Lagos")
    return datetime.now(lagos_tz)

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey('bookings.id'))  # Foreign key to bookings table
    room_number = Column(String, index=True)
    guest_name = Column(String, index=True)
    #booking_cost = Column(Float, nullable=True)  # Add the booking_cost column to Payment table
    amount_paid = Column(Float)
    discount_allowed = Column(Float)  # Discount allowed on the payment
    balance_due = Column(Float, default=0.0)
    payment_method = Column(String)
    #payment_date = Column(DateTime, default=get_local_time)  # Store with timezone
    #payment_date = Column(DateTime, default=datetime.utcnow)
    payment_date = Column(DateTime(timezone=True), server_default=func.now())  # ✅ Ensures correct timezone
    void_date = Column(DateTime, nullable=True, default=None)

    status = Column(String, default="pending")
    created_by = Column(String, nullable=False)  # Track who created the booking
    
    # Foreign key relationship to the booking
    booking = relationship("Booking", back_populates="payments")