from fastapi import FastAPI, Depends
from sqlmodel import Session
from database.connection import DatabaseManager

app = FastAPI()

@app.on_event("startup")
def on_startup():
    DatabaseManager.create_db_and_tables()

@app.get("/")
def root():
    return {"test"}