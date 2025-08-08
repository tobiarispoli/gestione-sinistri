from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from ..database import get_session
from ..models import Soggetto, SoggettoBase

router = APIRouter(prefix="/api/soggetti", tags=["Soggetti"])

@router.get("/", response_model=List[Soggetto])
def list_soggetti(session: Session = Depends(get_session)):
    return session.exec(select(Soggetto).order_by(Soggetto.id.desc())).all()

@router.post("/", response_model=Soggetto)
def create_soggetto(data: SoggettoBase, session: Session = Depends(get_session)):
    s = Soggetto.from_orm(data)
    session.add(s)
    session.commit()
    session.refresh(s)
    return s

@router.get("/{soggetto_id}", response_model=Soggetto)
def get_soggetto(soggetto_id: int, session: Session = Depends(get_session)):
    s = session.get(Soggetto, soggetto_id)
    if not s:
        raise HTTPException(404, "Soggetto non trovato")
    return s

@router.put("/{soggetto_id}", response_model=Soggetto)
def update_soggetto(soggetto_id: int, data: SoggettoBase, session: Session = Depends(get_session)):
    s = session.get(Soggetto, soggetto_id)
    if not s:
        raise HTTPException(404, "Soggetto non trovato")
    for k, v in data.dict().items():
        setattr(s, k, v)
    session.add(s)
    session.commit()
    session.refresh(s)
    return s

@router.delete("/{soggetto_id}")
def delete_soggetto(soggetto_id: int, session: Session = Depends(get_session)):
    s = session.get(Soggetto, soggetto_id)
    if not s:
        raise HTTPException(404, "Soggetto non trovato")
    session.delete(s)
    session.commit()
    return {"ok": True}