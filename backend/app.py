from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
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


origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://127.0.0.1:5000",
    "http://localhost:5000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(catalog_router)
app.include_router(quotation_router)


@app.get("/")
def root():
    return {"test"}