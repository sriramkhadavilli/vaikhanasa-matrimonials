import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Create database file path
db_path = os.path.join(os.getcwd(), "vaikhanasa.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create session local class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# ✅ Add this function so routes can access the database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
