from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.users.auth import get_current_user
from sqlalchemy.sql import func
from sqlalchemy import and_, or_, not_
from app.rooms import schemas as room_schemas, models as room_models, crud
from app.bookings import models as booking_models  # Adjust path if needed
from app.users import schemas
from sqlalchemy import func
from datetime import datetime


from typing import List


from app.rooms.models import RoomFault  # Not app.models.room
from app.rooms.schemas import RoomFaultOut , RoomStatusUpdate # Not app.schemas.room
from app.rooms.schemas import FaultUpdate


from datetime import date
from loguru import logger
import os


import pytz
from sqlalchemy.sql import func




router = APIRouter()

def get_local_time():
    lagos_tz = pytz.timezone("Africa/Lagos")
    return datetime.now(lagos_tz)

# Set up logging
logger.add("app.log", rotation="500 MB", level="DEBUG")


#log_path = os.path.join(os.getenv("LOCALAPPDATA", "C:\\Temp"), "app.log")
#logger.add("C:/Users/KLOUNGE/Documents/app.log", rotation="500 MB", level="DEBUG")




@router.post("/")
def create_room(
    room: schemas.RoomSchema,
    db: Session = Depends(get_db),
    current_user: schemas.UserDisplaySchema = Depends(get_current_user),
):
    
    logger.info(f"Room creation request received. User: {current_user.username}, Role: {current_user.role}")

    # Check for admin permissions
    if current_user.role != "admin":
        logger.warning(f"Permission denied for user {current_user.username}. Role: {current_user.role}")
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # Preserve the original case for storage but use lowercase for validation
    original_room_number = room.room_number
    normalized_room_number = original_room_number.lower()
    logger.debug(f"Original room number: {original_room_number}, Normalized room number: {normalized_room_number}")

    # Check if a room with the normalized room_number already exists
    existing_room = (
        db.query(room_models.Room)
        .filter(func.lower(room_models.Room.room_number) == normalized_room_number)
        .first()
    )
    if existing_room:
        logger.warning(f"Room creation failed. Room {original_room_number} already exists in the database.")
        raise HTTPException(status_code=400, detail="Room with this number already exists")

    logger.info(f"Creating a new room: {original_room_number}")

    try:
        # Create the room using the original case
        new_room = crud.create_room(db, room)
        logger.info(f"Room {original_room_number} created successfully.")
        return {"message": "Room created successfully", "room": new_room}
    except Exception as e:
        logger.error(f"Error while creating room {original_room_number}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while creating the room.")


@router.get("/", response_model=dict)
def list_rooms(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """
    Fetch a list of rooms with basic details: room number, room type, and amount.
    Also include the total number of rooms in the hotel.
    """
    # Fetch the list of rooms with pagination
    rooms = crud.get_rooms_with_pagination(skip=skip, limit=limit, db=db)
    
    # Convert SQLAlchemy rows to dictionaries
    serialized_rooms = crud.serialize_rooms(rooms)
    
    # Get the total count of rooms
    total_rooms = crud.get_total_room_count(db=db)
    
    # Return the response as a dictionary
    return {
        "total_rooms": total_rooms,  # Total number of rooms in the hotel
        "rooms": serialized_rooms,   # List of rooms
    }





import re

@router.get("/available")
def list_available_rooms(db: Session = Depends(get_db)):
    today = date.today()

    # Step 1: Get rooms not currently booked
    available_rooms_query = db.query(room_models.Room).filter(
        not_(
            room_models.Room.room_number.in_(
                db.query(booking_models.Booking.room_number)
                .filter(
                    booking_models.Booking.status.notin_(["checked-out", "cancelled"]),
                    and_(
                        booking_models.Booking.arrival_date <= today,
                        booking_models.Booking.departure_date >= today,
                    )
                )
            )
        )
    )

    all_available_rooms = available_rooms_query.all()
    total_rooms = db.query(room_models.Room).count()

    if not all_available_rooms:
        return {
            "message": "We are fully booked! No rooms are available for today.",
            "total_rooms": total_rooms,
            "total_available_rooms": 0,
            "available_rooms": [],
        }

    # Step 2: Prepare data for frontend
    serialized_rooms = []
    available_count = 0  # Exclude maintenance from this count

    for room in all_available_rooms:
        serialized_rooms.append({
            "room_number": room.room_number,
            "room_type": room.room_type,
            "amount": room.amount,
            "status": room.status
        })

        if room.status != "maintenance":
            available_count += 1

    # Helper for natural ascending sort
    def natural_sort_key(room):
        return [int(part) if part.isdigit() else part.lower()
                for part in re.split(r'(\d+)', room["room_number"])]

    # Sort both groups separately in ascending natural order
    available_sorted = sorted(
        [r for r in serialized_rooms if r["status"] != "maintenance"],
        key=natural_sort_key
    )
    maintenance_sorted = sorted(
        [r for r in serialized_rooms if r["status"] == "maintenance"],
        key=natural_sort_key
    )

    return {
        "message": "Available rooms fetched successfully.",
        "total_rooms": total_rooms,
        "total_available_rooms": available_count,
        "available_rooms": available_sorted + maintenance_sorted,
    }


@router.put("/faults/update")
def update_faults(faults: List[FaultUpdate], db: Session = Depends(get_db)):
    print("Received data:", faults)

    affected_rooms = set()

    for fault in faults:
        db_fault = db.query(RoomFault).filter(RoomFault.id == fault.id).first()
        if db_fault:
            if db_fault.resolved != fault.resolved:
                db_fault.resolved = fault.resolved
                if fault.resolved:
                    db_fault.resolved_at = get_local_time()
                else:
                    db_fault.resolved_at = None
            affected_rooms.add(db_fault.room_number)

    db.commit()

    # ✅ Re-check all faults for affected rooms
    for room_number in affected_rooms:
        unresolved = db.query(RoomFault).filter(
            RoomFault.room_number == room_number,
            RoomFault.resolved == False
        ).first()

        room = db.query(room_models.Room).filter(
            room_models.Room.room_number == room_number
        ).first()

        if room:
            if not unresolved and room.status == "maintenance":
                room.status = "available"
    db.commit()

    return {"message": "Faults updated successfully"}


@router.get("/{room_number}/faults", response_model=List[RoomFaultOut])
def get_room_faults(room_number: str, db: Session = Depends(get_db)):
    faults = db.query(RoomFault).filter(func.lower(RoomFault.room_number) == room_number.lower()).all()
    return [
        {
            "id": f.id,
            "room_number": f.room_number,
            "description": f.description,
            "resolved": f.resolved,
            "created_at": f.created_at.strftime('%Y-%m-%d %H:%M') if f.created_at else None,
            "resolved_at": f.resolved_at.strftime('%Y-%m-%d %H:%M') if f.resolved_at else None
        }
        for f in faults
    ]




#@router.put("/rooms/{room_number}/status")
@router.put("/{room_number}/status")
def update_room_status(
    room_number: str,
    status_update: RoomStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    room = db.query(room_models.Room).filter(
        func.lower(room_models.Room.room_number) == room_number.strip().lower()
    ).first()
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    room.status = status_update.status
    db.commit()
    return {"message": f"Room {room_number} status updated to {status_update.status}"}



@router.put("/{room_number}")
def update_room(
    room_number: str,
    room_update: room_schemas.RoomUpdateSchema,
    db: Session = Depends(get_db),
    current_user: schemas.UserDisplaySchema = Depends(get_current_user),
):
    #if current_user.role != "admin":
        #raise HTTPException(status_code=403, detail="Insufficient permissions")

    room_number = room_number.lower()
    room = db.query(room_models.Room).filter(func.lower(room_models.Room.room_number) == room_number).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if room.status == "checked-in":
        raise HTTPException(
            status_code=400,
            detail="Room cannot be updated as it is currently checked-in"
        )

    if room_update.room_number and room_update.room_number.lower() != room.room_number.lower():
        existing_room = db.query(room_models.Room).filter(
            func.lower(room_models.Room.room_number) == room_update.room_number.lower()
        ).first()
        if existing_room:
            raise HTTPException(status_code=400, detail="Room with this number already exists")
        room.room_number = room_update.room_number.lower()

    if room_update.room_type:
        room.room_type = room_update.room_type

    if room_update.amount is not None:
        room.amount = room_update.amount

    if room_update.status:
        if room_update.status not in ["available", "maintenance"]:
            raise HTTPException(status_code=400, detail="Invalid status value")
        room.status = room_update.status

    # ✅ Process faults
    if room_update.faults is not None:
        for fault_data in room_update.faults:
            if fault_data.id is not None:
                existing_fault = db.query(room_models.RoomFault).filter(
                    room_models.RoomFault.id == fault_data.id,
                    room_models.RoomFault.room_number == room.room_number
                ).first()
                if existing_fault:
                    existing_fault.resolved = fault_data.resolved
                    existing_fault.description = fault_data.description
            else:
                new_fault = room_models.RoomFault(
                    room_number=room.room_number,
                    description=fault_data.description,
                    resolved=fault_data.resolved if fault_data.resolved is not None else False
                )
                db.add(new_fault)

    db.commit()

    # ✅ Re-check all faults after commit
    unresolved_faults = db.query(room_models.RoomFault).filter(
        room_models.RoomFault.room_number == room.room_number,
        room_models.RoomFault.resolved == False
    ).all()

    if not unresolved_faults:
        room.status = "available"

    db.commit()
    db.refresh(room)

    return {
        "message": "Room updated successfully",
        "room": {
            "room_number": room.room_number,
            "room_type": room.room_type,
            "amount": room.amount,
            "status": room.status,
            "faults": [
                {
                    "id": fault.id,
                    "description": fault.description,
                    "resolved": fault.resolved,
                    "room_number": room.room_number
                }
                for fault in room.faults
            ]
        }
    }





@router.get("/{room_number}")
def get_room(room_number: str, db: Session = Depends(get_db)):
    logger.info(f"Fetching room with room_number: {room_number}")

    try:
        if not room_number:
            logger.warning("Room number is missing in the request")
            raise HTTPException(status_code=400, detail="Room number is required")

        # Normalize input
        normalized_room_number = room_number.strip().lower()
        logger.debug(f"Normalized room number: {normalized_room_number}")

        # Query the room details
        room = db.query(room_models.Room).filter(
            room_models.Room.room_number.ilike(normalized_room_number)
        ).first()

        if not room:
            logger.warning(f"Room {room_number} not found.")
            raise HTTPException(status_code=404, detail="Room not found")

        # Fetch the latest active booking for this room
        latest_booking = (
            db.query(booking_models.Booking)
            .filter(
                booking_models.Booking.room_number.ilike(normalized_room_number),
                booking_models.Booking.status.notin_(["checked-out", "cancelled"])
            )
            .order_by(booking_models.Booking.booking_date.desc())  # Get the most recent booking
            .first()
        )

        # Get the booking type if a booking exists, otherwise return "No active booking"
        booking_type = latest_booking.booking_type if latest_booking else "No active booking"

        logger.info(f"Successfully fetched room: {room.room_number}, Booking Type: {booking_type}")

        return {
            "room_number": room.room_number,
            "room_type": room.room_type,
            "amount": room.amount,
            "status": room.status,
            "booking_type": booking_type
        }

    except HTTPException as http_err:
        raise http_err  # Re-raise known HTTP exceptions

    except Exception as e:
        logger.error(f"Unexpected error fetching room {room_number}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred")



@router.get("/summary")
def room_summary(
    db: Session = Depends(get_db),
    current_user: schemas.UserDisplaySchema = Depends(get_current_user),
):
    """
    Generate a summary of all rooms, including counts of:
    - Checked-in rooms
    - Reserved rooms (both today and future, counted separately)
    - Available rooms for today
    """
    today = date.today()

    try:
        # Total number of rooms
        total_rooms = db.query(room_models.Room).count()

        # Checked-in rooms today
        total_checked_in_rooms = (
            db.query(booking_models.Booking)
            .filter(
                booking_models.Booking.status == "checked-in",
                booking_models.Booking.arrival_date <= today,
                booking_models.Booking.departure_date >= today,
            )
            .count()
        )

        # Reserved rooms (count reservations separately)
        total_reserved_rooms = (
            db.query(booking_models.Booking)
            .filter(
                booking_models.Booking.status == "reserved",
                booking_models.Booking.arrival_date >= today,
            )
            .count()
        )

        # Occupied rooms today (checked-in + reserved for today)
        occupied_rooms_today = (
            db.query(booking_models.Booking.room_number)
            .filter(
                or_(
                    booking_models.Booking.status == "checked-in",
                    and_(
                        booking_models.Booking.status == "reserved",
                        booking_models.Booking.arrival_date <= today,
                        booking_models.Booking.departure_date >= today,
                    ),
                )
            )
            .distinct()
            .all()
        )
        occupied_room_numbers_today = {room.room_number for room in occupied_rooms_today}

        # Total available rooms
        total_available_rooms = total_rooms - len(occupied_room_numbers_today)

        # Determine the appropriate message
        message = (
            f"{total_available_rooms} room(s) available."
            if total_available_rooms > 0
            else "Fully booked! All rooms are occupied for today."
        )

        return {
            "total_rooms": total_rooms,
            "rooms_checked_in": total_checked_in_rooms,
            "rooms_reserved": total_reserved_rooms,
            "rooms_available": total_available_rooms,
            "message": message,
        }

    except Exception as e:
        logger.error(f"Error generating room summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching room summary: {str(e)}",
        )



@router.delete("/{room_number}")
def delete_room(
    room_number: str,
    db: Session = Depends(get_db),
    current_user: schemas.UserDisplaySchema = Depends(get_current_user),
):
    # Ensure only admin can delete rooms
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # Normalize the room_number input to lowercase
    room_number = room_number.lower()

    # Fetch the room by the normalized room_number
    room = db.query(room_models.Room).filter(func.lower(room_models.Room.room_number) == room_number).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Check if the room is tied to any bookings
    bookings = db.query(booking_models.Booking).filter(
        func.lower(booking_models.Booking.room_number) == room_number
    ).all()
    if bookings:
        raise HTTPException(
            status_code=400,
            detail=f"Room {room_number} cannot be deleted as it is tied to one or more bookings."
        )

    # Delete the room if it is available
    try:
        db.delete(room)
        db.commit()
        return {"message": f"Room {room_number} deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while deleting the room: {str(e)}"
        )