from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.routing import APIRoute
from app.database import engine, Base
from app.users.router import router as user_router
from app.rooms.router import router as rooms_router
from app.bookings.router import router as bookings_router
from app.payments.router import router as payments_router
from app.license.router import router as license_router
from app.events.router import router as events_router
from app.eventpayment.router import router as eventpayment_router
from backup.backup import router as backup_router


from app.store.router import router as store_router
from app.bar.routers import router as bar_router
from app.barpayment.router import router as barpayment_router
from app.vendor.router import router as vendor_router


import uvicorn
import os
import sys
import pytz
from datetime import datetime
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()

SERVER_IP = os.getenv("SERVER_IP", "127.0.0.1")
print("Running on SERVER_IP:", SERVER_IP)


# Ensure upload folder exists
os.makedirs("uploads/attachments", exist_ok=True)

# Set default timezone to Africa/Lagos
os.environ["TZ"] = "Africa/Lagos"
lagos_tz = pytz.timezone("Africa/Lagos")
current_time = datetime.now(lagos_tz)

# Adjust sys path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Database startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup")
    Base.metadata.create_all(bind=engine)
    yield
    print("Application shutdown")

# Create app
app = FastAPI(
    title="Hotel & Event Management System",
    description="An API for managing hotel operations including Bookings, Reservations, Rooms, and Payments.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, change to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Static files (uploads)
app.mount("/files", StaticFiles(directory="uploads"), name="files")
#app.mount("/attachments", StaticFiles(directory="uploads/attachments"), name="attachments")

# Static React frontend
react_build_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "react-frontend", "build"))
react_static_dir = os.path.join(react_build_dir, "static")
app.mount("/static", StaticFiles(directory=react_static_dir), name="static")

# Routers
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(rooms_router, prefix="/rooms", tags=["Rooms"])
app.include_router(bookings_router, prefix="/bookings", tags=["Bookings"])
app.include_router(payments_router, prefix="/payments", tags=["Payments"])
app.include_router(events_router, prefix="/events", tags=["Events"])
app.include_router(eventpayment_router, prefix="/eventpayment", tags=["Event_Payments"])
app.include_router(license_router, prefix="/license", tags=["License"])
app.include_router(backup_router)


app.include_router(store_router, prefix="/store", tags=["Store"])
app.include_router(bar_router, prefix="/bar", tags=["Bar"])
app.include_router(barpayment_router, prefix="/barpayment", tags=["Bar Payment"])
app.include_router(vendor_router, prefix="/vendor", tags=["Vendor"])



# Simple health check
@app.get("/debug/ping")
def debug_ping():
    return {"status": "ok"}

# ✅ Route fallback for SPA (React frontend)
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    # Skip fallback for known API/static routes
    known_paths = [route.path for route in app.routes if isinstance(route, APIRoute)]
    if any(full_path == path.strip("/") or full_path.startswith(path.strip("/") + "/") for path in known_paths):
        return JSONResponse(status_code=404, content={"detail": "This is an API route, not SPA."})

    index_file = os.path.join(react_build_dir, "index.html")
    return FileResponse(index_file)

# Entry point
if __name__ == "__main__":
    
    uvicorn.run("app.main:app", host=SERVER_IP, port=8000, log_level="info", access_log=False)


