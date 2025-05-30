

from app.database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import date





# app/rooms/models.py

class RoomFault(Base):
    __tablename__ = "room_faults"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String, ForeignKey("rooms.room_number", ondelete="CASCADE"))
    description = Column(String)
    resolved = Column(Boolean, default=False)

    created_at = Column(Date, default=date.today)
    resolved_at = Column(Date, nullable=True)
    #room = relationship("Room", back_populates="faults")  # Ensure this is defined

    room = relationship("Room", back_populates="faults", foreign_keys=[room_number])


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String, unique=True, nullable=False)
    room_type = Column(String(50))
    amount = Column(Integer)
    status = Column(String(50))  # "available" or "maintenance"

    bookings = relationship("Booking", back_populates="room")
    faults = relationship("RoomFault", back_populates="room", cascade="all, delete-orphan", foreign_keys=[RoomFault.room_number])
    
    

