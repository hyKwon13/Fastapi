from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import user, item, admin, websocket
from app.database import engine, Base

app = FastAPI(docs_url=None, redoc_url=None)

app.mount("/static", StaticFiles(directory="static"), name="static")

Base.metadata.create_all(bind=engine)

app.include_router(user.router)
app.include_router(item.router)
app.include_router(admin.router)
app.include_router(websocket.router)