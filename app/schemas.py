from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

class UserCreate(BaseModel):
    # Basic
    name: str
    email: EmailStr
    phone: str
    gender: str
    age: int
    password: str
    country: str
    city: str

    # Traditional
    gotra: str
    nakshatra: str
    raasi: Optional[str] = None
    sub_sakha: Optional[str] = None

    # Education & Career
    education: Optional[str] = None
    profession: Optional[str] = None
    work_location: Optional[str] = None
    organization: Optional[str] = None

    # Personal Details
    dob: Optional[str] = None
    pob: Optional[str] = None
    height: Optional[str] = None
    complexion: Optional[str] = None
    salary: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    gender: str
    age: int
    country: str
    city: str
    photo: Optional[str]

    model_config = ConfigDict(from_attributes=True)
