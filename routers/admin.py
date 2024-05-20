from fastapi import APIRouter, Request, Depends, HTTPException, Path, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session, joinedload
from app.models import User, GroupedItem
from app.database import get_db
from app.dependencies import get_current_admin_user

router = APIRouter()

@router.get("/admin/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    users = db.query(User).all()
    return templates.TemplateResponse("admin_dashboard.html", {"request": request, "users": users})

@router.post("/admin/approve/{user_id}")
async def admin_approve_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_approved = True
    db.commit()
    return RedirectResponse(url="/admin/", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/admin/delete/{user_id}")
async def admin_delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return RedirectResponse(url="/admin/", status_code=status.HTTP_303_SEE_OTHER)

@router.put("/release_item/{grouped_item_id}")
async def release_item(grouped_item_id: int = Path(...), db: Session = Depends(get_db)):
    grouped_item = db.query(GroupedItem).filter(GroupedItem.id == grouped_item_id).options(joinedload(GroupedItem.items)).first()
    if grouped_item:
        for item in grouped_item.items:
            if item.status == "출고대기":
                item.status = "출고완료"
        db.commit()
        return {"message": "그룹화된 품목들 출고 완료"}
    else:
        raise HTTPException(status_code=404, detail="그룹을 찾을 수 없습니다.")