from pydantic import BaseModel, EmailStr, ConfigDict

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    gender: str
    age: int
    password: str
    country: str
    city: str
    gotra: str
    nakshatra: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    gender: str
    age: int

    model_config = ConfigDict(from_attributes=True)  # Replaces orm_mode
