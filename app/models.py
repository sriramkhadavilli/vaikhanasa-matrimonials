from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String, unique=True)
    gender = Column(String)
    age = Column(Integer)
    password = Column(String)
    country = Column(String)
    city = Column(String)
    gotra = Column(String)
    nakshatra = Column(String)
    is_admin = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    photo = Column(String, default="default.jpg")  # 👈 NEW field added for profile photo

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    matched_user_id = Column(Integer, ForeignKey("users.id"))
