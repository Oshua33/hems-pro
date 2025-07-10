import os
from datetime import datetime
from fastapi import APIRouter, Response
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import subprocess

load_dotenv()

router = APIRouter()

DB_URL = os.getenv("DB_URL")
BACKUP_DIR = os.path.join(os.getcwd(), "backup_files")
os.makedirs(BACKUP_DIR, exist_ok=True)

@router.get("/backup/db")
def backup_database():
    if not DB_URL.startswith("postgresql://"):
        return {"error": "Only PostgreSQL backups are supported."}

    try:
        db_user = DB_URL.split("//")[1].split(":")[0]
        db_name = DB_URL.rsplit("/", 1)[-1]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"hems_backup_{timestamp}.sql"
        filepath = os.path.join(BACKUP_DIR, filename)

        command = [
            r"C:\Program Files\PostgreSQL\15\bin\pg_dump.exe",
            "-U", db_user,
            "-F", "c",  # Custom format
            "-f", filepath,
            db_name
        ]

        env = os.environ.copy()
        env["PGPASSWORD"] = DB_URL.split(":")[2].split("@")[0]  # extract password

        subprocess.run(command, env=env, check=True)

        return FileResponse(
            path=filepath,
            media_type="application/octet-stream",
            filename=filename
        )
    except Exception as e:
        return {"error": str(e)}
