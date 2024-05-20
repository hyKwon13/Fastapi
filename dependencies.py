from fastapi import Request, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
from .auth import get_current_user_from_token

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token is required")
    
    user_id = get_current_user_from_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_current_admin_user(request: Request, db: Session = Depends(get_db)) -> User:
    user = get_current_user(request, db)
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user