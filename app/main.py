from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.users.router import router as user_router
from app.rooms.router import router as rooms_router
from app.bookings.router import router as bookings_router
from app.payments.router import router as payments_router
from app.license.router import router as license_router
from app.events.router import router as events_router
from app.eventpayment.router import router as eventpayment_router
import uvicorn
import sys
import os
from fastapi.staticfiles import StaticFiles
#from app.bookings import router as booking_router


import pytz
from datetime import datetime


os.makedirs("uploads/attachments", exist_ok=True)



# Set Africa/Lagos as default timezone in your Python application
os.environ["TZ"] = "Africa/Lagos"

# Convert UTC to Africa/Lagos
lagos_tz = pytz.timezone("Africa/Lagos")
current_time = datetime.now(lagos_tz)

#print("Africa/Lagos Time:", current_time)



from contextlib import asynccontextmanager




sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup")
    Base.metadata.create_all(bind=engine)  # Database initialization
    yield
    print("Application shutdown")


# ✅ Only one FastAPI instance
app = FastAPI(
    title="Hotel & Event Management System",
    description="An API for managing hotel operations including Bookings, Reservations, Rooms, and Payments.",
    version="1.0.0",
    lifespan=lifespan
)

app.mount("/files", StaticFiles(directory="uploads"), name="files")

# ✅ Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000"],  # Change if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Include all routers
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(rooms_router, prefix="/rooms", tags=["Rooms"])
app.include_router(bookings_router, prefix="/bookings", tags=["Bookings"])
app.include_router(payments_router, prefix="/payments", tags=["Payments"])
app.include_router(events_router, prefix="/events", tags=["Events"])
app.include_router(eventpayment_router, prefix="/eventpayment", tags=["Event_Payments"])
app.include_router(license_router, prefix="/license", tags=["License"])


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, log_level="info")

@app.get("/debug/ping")
def debug_ping():
    return {"status": "ok"}
