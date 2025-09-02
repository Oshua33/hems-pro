import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ✅ Load .env from project root (fallback to script directory if needed)
env_path = Path('.') / '.env'
if not env_path.exists():
    env_path = Path(__file__).resolve().parent.parent / '.env'  # try from root directory

load_dotenv()
os.getenv("DB_URL")

load_dotenv(dotenv_path=env_path)
print(f"🔄 Loaded environment from: {env_path}")

# ✅ Get database URL from environment
SQLALCHEMY_DATABASE_URL = os.getenv("DB_URL2")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# ✅ Validate environment values
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("❌ DB_URL environment variable is not set!")

# ✅ Show current DB connection string (partial for security)
print(f"🔍 Using database: {SQLALCHEMY_DATABASE_URL.split('@')[-1]}")

# ✅ Set up SQLAlchemy
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ✅ Dependency for FastAPI routes
def get_db():
    """Provide a transactional scope around a series of operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
