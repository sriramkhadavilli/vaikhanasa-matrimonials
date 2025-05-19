import os
import shutil
from pathlib import Path
from fastapi import FastAPI, Request, Form, Depends, File, UploadFile, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app import models, auth
from app.database import engine, SessionLocal
from app.routes import user_routes

BASE_DIR = Path(__file__).resolve().parent.parent

# Global session stores
logged_in_user = {"user": None}
admin_session = {"admin": None}

app = FastAPI()

# DB setup
models.Base.metadata.create_all(bind=engine)
app.include_router(user_routes.router)

# Template and static file setup
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "user": logged_in_user["user"]
    })

@app.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register-form")
async def register_user_form(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    gender: str = Form(...),
    age: int = Form(...),
    password: str = Form(...),
    country: str = Form(...),
    city: str = Form(...),
    gotra: str = Form(...),
    nakshatra: str = Form(...),
    raasi: str = Form(None),
    sub_sakha: str = Form(None),
    dob: str = Form(None),
    pob: str = Form(None),
    height: str = Form(None),
    complexion: str = Form(None),
    salary: str = Form(None),
    education: str = Form(None),
    profession: str = Form(None),
    work_location: str = Form(None),
    organization: str = Form(None),
    photo: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    existing_user = db.query(models.User).filter(models.User.email == email).first()
    if existing_user:
        return HTMLResponse("<h3 style='color:red;'>Email already registered.</h3>", status_code=400)

    filename = "default.jpg"
    if photo and photo.filename:
        uploads_dir = os.path.join("static", "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        filename = f"{email.replace('@', '_')}.jpg"
        with open(os.path.join(uploads_dir, filename), "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)

    hashed_pw = auth.hash_password(password)
    user = models.User(
        name=name,
        email=email,
        phone=phone,
        gender=gender,
        age=age,
        password=hashed_pw,
        country=country,
        city=city,
        gotra=gotra,
        nakshatra=nakshatra,
        raasi=raasi,
        sub_sakha=sub_sakha,
        dob=dob,
        pob=pob,
        height=height,
        complexion=complexion,
        salary=salary,
        education=education,
        profession=profession,
        work_location=work_location,
        organization=organization,
        photo=filename
    )

    db.add(user)
    db.commit()
    return RedirectResponse("/login", status_code=302)

@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login-form")
async def login_user_form(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if user and auth.verify_password(password, user.password):
        logged_in_user["user"] = user
        return RedirectResponse("/profile", status_code=302)
    return HTMLResponse("<h3>Invalid credentials</h3>", status_code=401)

@app.get("/profile", response_class=HTMLResponse)
def profile(request: Request):
    if not logged_in_user["user"]:
        return RedirectResponse("/login")
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": logged_in_user["user"]
    })

@app.get("/logout")
def logout():
    logged_in_user["user"] = None
    admin_session["admin"] = None
    return RedirectResponse("/login", status_code=302)

# Admin login and approval logic remains unchanged
# You can copy it from your original file unless you want that part redesigned too
