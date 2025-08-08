from fastapi import FastAPI
from sqlmodel import SQLModel
from app.database import engine
from app.routes import coinvolgimenti  # il nuovo router che gestisce Coinvolgimenti

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

