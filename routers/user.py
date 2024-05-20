from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.models import User
from app.database import get_db
from app.auth import hash_password, create_jwt_token, verify_password
from app.dependencies import get_current_user

router = APIRouter()

@router.get("/login/", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register/", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register/", response_class=HTMLResponse)
async def register_user(request: Request, username: str = Form(...), position: str = Form(...), password: str = Form(...)):
    db = get_db()
    user_by_username = db.query(User).filter(User.username == username).first()
    if user_by_username:
        error_message = "이미 사용 중인 사용자 이름입니다."
        return templates.TemplateResponse("register.html", {"request": request, "error_message": error_message})
    hashed_password = hash_password(password)
    new_user = User(username=username, position=position, password=hashed_password)
    db.add(new_user)
    db.commit()
    return templates.TemplateResponse("registration_success.html", {"request": request})

@router.post("/token/")
async def login_user(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    db = get_db()
    user = db.query(User).filter(User.username == form_data.username).first()
    if user is None or not verify_password(form_data.password, user.password):
        return templates.TemplateResponse("login.html", {"request": request, "error_message2": "Invalid credentials"})
    token = create_jwt_token(user.id, user.username)
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
    return response

@router.get("/logout/")
async def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    return response