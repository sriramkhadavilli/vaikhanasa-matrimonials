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

@app.get("/matches", response_class=HTMLResponse)
def match_suggestions(
    request: Request,
    gender: str = Query(None),
    gotra: str = Query(None),
    nakshatra: str = Query(None),
    min_age: str = Query(None),
    max_age: str = Query(None),
    country: str = Query(None),
    city: str = Query(None),
    db: Session = Depends(get_db)
):
    user = logged_in_user["user"]
    if not user:
        return RedirectResponse("/login", status_code=302)

    query = db.query(models.User).filter(
        models.User.id != user.id,
        models.User.is_approved == True
    )

    if gender:
        query = query.filter(models.User.gender == gender)
    if gotra:
        query = query.filter(models.User.gotra == gotra)
    if nakshatra:
        query = query.filter(models.User.nakshatra == nakshatra)
    if min_age and min_age.isdigit():
        query = query.filter(models.User.age >= int(min_age))
    if max_age and max_age.isdigit():
        query = query.filter(models.User.age <= int(max_age))
    if country:
        query = query.filter(models.User.country == country)
    if city:
        query = query.filter(models.User.city == city)

    matches = query.all()
    return templates.TemplateResponse("matches.html", {
        "request": request,
        "user": user,
        "matches": matches
    })

@app.get("/gallery", response_class=HTMLResponse)
def public_gallery(request: Request, page: int = 1, db: Session = Depends(get_db)):
    if not logged_in_user["user"]:
        return RedirectResponse("/login", status_code=302)

    page_size = 6
    offset = (page - 1) * page_size

    total_users = db.query(models.User).filter(models.User.is_approved == True).count()
    approved_users = db.query(models.User).filter(models.User.is_approved == True).offset(offset).limit(page_size).all()
    total_pages = (total_users + page_size - 1) // page_size

    return templates.TemplateResponse("gallery.html", {
        "request": request,
        "users": approved_users,
        "current_page": page,
        "total_pages": total_pages
    })

@app.get("/user/{user_id}", response_class=HTMLResponse)
def view_user_profile(user_id: int, request: Request, db: Session = Depends(get_db)):
    if not logged_in_user["user"]:
        return RedirectResponse("/login", status_code=302)

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or not user.is_approved:
        return HTMLResponse("<h3>User not found or not approved.</h3>", status_code=404)

    return templates.TemplateResponse("public_profile.html", {
        "request": request,
        "user": user
    })

@app.get("/logout")
def logout():
    logged_in_user["user"] = None
    admin_session["admin"] = None
    return RedirectResponse("/login", status_code=302)

@app.get("/admin", response_class=HTMLResponse)
def show_admin_login(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

@app.post("/admin-login")
def admin_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    admin = db.query(models.User).filter(
        models.User.email == email,
        models.User.is_admin == True
    ).first()

    if admin and auth.verify_password(password, admin.password):
        admin_session["admin"] = admin
        return RedirectResponse("/admin-panel", status_code=302)

    return HTMLResponse("<h3>Invalid admin credentials</h3>", status_code=401)

@app.get("/admin-panel", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    if not admin_session["admin"]:
        return RedirectResponse("/admin", status_code=302)

    users = db.query(models.User).filter(models.User.is_admin == False).all()
    return templates.TemplateResponse("admin_panel.html", {
        "request": request,
        "users": users
    })

@app.get("/approve/{user_id}")
def approve_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.is_approved = True
        db.commit()
        send_email(user.email, "Profile Approved", f"Hello {user.name}, your profile is now live!")
    return RedirectResponse("/admin-panel", status_code=302)

@app.get("/create-admin")
def create_admin_user(db: Session = Depends(get_db)):
    from app.auth import hash_password
    existing = db.query(models.User).filter(models.User.email == "admin@vaikhanasa.com").first()
    if existing:
        return {"message": "Admin already exists"}

    admin = models.User(
        name="Admin",
        email="admin@vaikhanasa.com",
        phone="0000000000",
        gender="Other",
        age=99,
        password=hash_password("admin123"),
        country="India",
        city="Admin",
        gotra="None",
        nakshatra="None",
        is_admin=True,
        is_approved=True,
        photo=""
    )
    db.add(admin)
    db.commit()
    return {"message": "Admin created"}

def send_email(to_email: str, subject: str, body: str):
    print(f"[EMAIL] To: {to_email}\nSubject: {subject}\n\n{body}")
