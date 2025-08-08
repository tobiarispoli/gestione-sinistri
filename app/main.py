from fastapi import FastAPI
from sqlmodel import SQLModel
from .database import engine
from .routes import coinvolgimenti

app = FastAPI(title="Gestione Sinistri")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

app.include_router(coinvolgimenti.router)

@app.get("/")
def home():
    return {"status": "ok"}
