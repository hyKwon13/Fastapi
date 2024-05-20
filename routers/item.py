from fastapi import APIRouter, Request, Form, Query, Depends, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func
from datetime import datetime, date
from typing import List, Tuple
from app.models import Item, GroupedItem, User
from app.schemas import ItemModel
from app.database import get_db
from app.dependencies import get_current_user
import csv
import json

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request, page: int = Query(1, ge=1), size: int = Query(10, le=100), db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    is_admin = current_user.is_admin
    username = current_user.username
    position = current_user.position

    total_items = db.query(GroupedItem).count()
    items = db.query(GroupedItem).options(joinedload(GroupedItem.items)).order_by(GroupedItem.created_at.desc()).offset((page - 1) * size).limit(size).all()

    for grouped_item in items:
        statuses = [item.status for item in grouped_item.items]
        if all(status == "출고대기" for status in statuses):
            grouped_item.aggregated_status = "출고대기"
        elif "출고대기" not in statuses:
            grouped_item.aggregated_status = "출고완료"
        else:
            grouped_item.aggregated_status = "출고중"

    total_pages = (total_items - 1) // size + 1

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "inventory": items,
            "page": page,
            "size": size,
            "total_pages": total_pages,
            "current_user": current_user.id,
            "current_user2": username,
            "position": position,
            "is_admin": is_admin
        }
    )

@router.post("/add_item/")
async def add_item(request: Request, page: int = Query(1, ge=1), size: int = Query(10, le=100), db: Session = Depends(get_db)):
    form_data = await request.form()
    current_user = get_current_user(request, db)

    vendor = form_data.get("vendor", "-")
    address = form_data.get("address", "-")
    recipient = form_data.get("recipient", "-")
    phone_number = form_data.get("phone_number", "-")
    note = form_data.get("note", "-")
    username = current_user.username
    position = current_user.position

    cargo_type = form_data["cargo_type"] if form_data["cargo_type"] != "기타" else form_data.get("custom_cargo_type")
    products = form_data.getlist("product[]")
    quantities = form_data.getlist("quantity[]")
    product = [(p, int(q)) for p, q in zip(products, quantities)]

    grouped_item = db.query(GroupedItem).filter(GroupedItem.vendor == vendor, GroupedItem.cargo_type == cargo_type, GroupedItem.created_at == func.current_timestamp()).first()
    if not grouped_item:
        grouped_item = GroupedItem(vendor=vendor, cargo_type=cargo_type, total_quantity=0)
        db.add(grouped_item)
        db.commit()
        db.refresh(grouped_item)

    for p, q in product:
        db_item = Item(vendor=vendor, address=address, recipient=recipient, phone_number=phone_number, note=note, product=p, quantity=q, cargo_type=cargo_type, username=username, position=position, grouped_item=grouped_item)
        grouped_item.total_quantity += q
        db.add(db_item)
        db.commit()
        db.refresh(db_item)

    items = db.query(Item).filter(Item.grouped_item_id == grouped_item.id).order_by(Item.created_at.desc()).offset((page - 1) * size).limit(size).all()

    for websocket in connected_websockets:
        new_item_info = {
            "message": "새 아이템이 추가되었습니다.",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cargo_type": cargo_type,
            "vendor": vendor,
            "username": username,
            "position": position
        }
        await websocket.send_text(json.dumps(new_item_info))

    redirect_url = f"/?page={page}&size={size}"
    return templates.TemplateResponse("redirect.html", {"request": request, "redirect_url": redirect_url})

@router.get("/items/", response_model=List[ItemModel])
async def read_items(db: Session = Depends(get_db)):
    today = date.today()
    db_items = db.query(Item).filter(func.date(Item.created_at) == today).all()
    items = [ItemModel.from_orm(db_item) for db_item in db_items]
    return items

@router.get("/items/by_date_range/")
async def read_items_by_date_range(start_date: date = Query(...), end_date: date = Query(...), db: Session = Depends(get_db)):
    end_datetime = datetime.combine(end_date, datetime.max.time())
    db_items = db.query(Item).filter(Item.created_at >= start_date, Item.created_at <= end_datetime).all()
    items_data = [{"vendor": item.vendor, "address": item.address, "recipient": item.recipient, "phone_number": item.phone_number, "note": item.note, "product": item.product, "quantity": item.quantity, "cargo_type": item.cargo_type, "created_at": item.created_at, "status": item.status, "username": item.username, "position": item.position, "grouped_item_id": item.grouped_item_id} for item in db_items]
    return items_data

@router.get("/download_csv/", response_class=StreamingResponse)
async def download_csv(request: Request):
    with SessionLocal() as session:
        items = session.query(Item).all()

    filename = datetime.now().strftime("items_%y%m%d%H%M%S.csv")
    with open(filename, mode="w", newline="", encoding="utf-8-sig") as csvfile:
        fieldnames = ["created_at", "username", "position", "cargo_type", "vendor", "address", "recipient", "phone_number", "note", "product", "quantity", "status", "grouped_item_id"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for item in items:
            writer.writerow({"created_at": item.created_at, "username": item.username, "position": item.position, "cargo_type": item.cargo_type, "vendor": item.vendor, "address": item.address, "recipient": item.recipient, "phone_number": item.phone_number, "note": item.note, "product": item.product, "quantity": item.quantity, "status": item.status, "grouped_item_id": item.grouped_item_id})

    file_stream = open(filename, mode="rb")
    response = StreamingResponse(file_stream, media_type="application/octet-stream")
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response