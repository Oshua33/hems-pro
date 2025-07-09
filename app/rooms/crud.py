from sqlalchemy.orm import Session
from app.rooms import models, schemas
from app.rooms import models as room_models


def create_room(db: Session, room: schemas.RoomSchema):
    db_room = models.Room(
        room_number=room.room_number,
        room_type=room.room_type,
        amount=room.amount,
        status=room.status
    )
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room




def get_rooms_with_pagination(skip: int, limit: int, db: Session):
    return (
        db.query(room_models.Room)
        .order_by(room_models.Room.id.asc())  # 🔼 Ensure ascending order by ID
        .offset(skip)
        .limit(limit)
        .all()
    )


# crud.py
def serialize_rooms(rooms):
    """
    Convert Room SQLAlchemy objects (optionally joined with additional info)
    to JSON-serializable dicts.
    """
    serialized = []
    for room in rooms:
        if room.id is None:
            continue  # skip corrupted entries

        # Support attributes that might be dynamically added (e.g., via joins or annotations)
        payment_status = getattr(room, "payment_status", None)
        future_reservation_count = getattr(room, "future_reservation_count", 0)

        serialized.append({
            "id": room.id,
            "room_number": room.room_number,
            "room_type": room.room_type,
            "amount": room.amount,
            "status": room.status,
            #"payment_status": payment_status,
            "future_reservation_count": future_reservation_count,
        })

    return serialized


    

def get_total_room_count(db: Session):
    """
    Fetch the total number of rooms in the hotel.
    """
    return db.query(room_models.Room).count()
