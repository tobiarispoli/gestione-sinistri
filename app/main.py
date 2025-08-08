from fastapi import FastAPI
from sqlmodel import SQLModel
from .database import engine
from .routes import coinvolgimenti

app = FastAPI(title="Gestione Sinistri")

# Creazione tabelle al primo avvio
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# Inclusione router Coinvolgimenti
app.include_router(coinvolgimenti.router, prefix="/api", tags=["Coinvolgimenti"])

# Rotta di test
@app.get("/")
def home():
    return {"status": "ok"}
