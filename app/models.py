from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Basic Info
    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String, unique=True)
    gender = Column(String)
    age = Column(Integer)
    password = Column(String)

    # Location
    country = Column(String)
    city = Column(String)

    # Traditional Fields
    gotra = Column(String)
    nakshatra = Column(String)
    raasi = Column(String)
    sub_sakha = Column(String)

    # Education & Career
    education = Column(String)
    profession = Column(String)
    work_location = Column(String)
    organization = Column(String)

    # Personal Profile
    dob = Column(String)  # Date & time of birth
    pob = Column(String)  # Place & District of Birth
    height = Column(String)
    complexion = Column(String)
    salary = Column(String)

    # System Fields
    is_admin = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    photo = Column(String, default="default.jpg")


class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    matched_user_id = Column(Integer, ForeignKey("users.id"))
