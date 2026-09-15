from fastapi import FastAPI, Depends
from sqlmodel import Session
from database.connection import DatabaseManager

from routers.admin import router as admin_router
from routers.auth import router as auth_router
from routers.catalog import router as catalog_router
from routers.quotation import router as quotation_router

app = FastAPI()

@app.on_event("startup")
def on_startup():
    DatabaseManager.create_db_and_tables()



app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(catalog_router)
app.include_router(quotation_router)


@app.get("/")
def root():
    return {"test"}