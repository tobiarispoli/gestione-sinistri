from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from ..database import get_session
from ..models import Scadenza, ScadenzaBase

router = APIRouter(prefix="/api/scadenze", tags=["Scadenze"])

@router.get("/", response_model=List[Scadenza])
def list_scadenze(session: Session = Depends(get_session)):
    return session.exec(select(Scadenza).order_by(Scadenza.id.desc())).all()

@router.post("/", response_model=Scadenza)
def create_scadenza(data: ScadenzaBase, session: Session = Depends(get_session)):
    s = Scadenza.from_orm(data)
    session.add(s)
    session.commit()
    session.refresh(s)
    return s

@router.put("/{scad_id}", response_model=Scadenza)
def update_scadenza(scad_id: int, data: ScadenzaBase, session: Session = Depends(get_session)):
    s = session.get(Scadenza, scad_id)
    if not s:
        raise HTTPException(404, "Scadenza non trovata")
    for k, v in data.dict().items():
        setattr(s, k, v)
    session.add(s)
    session.commit()
    session.refresh(s)
    return s

@router.delete("/{scad_id}")
def delete_scadenza(scad_id: int, session: Session = Depends(get_session)):
    s = session.get(Scadenza, scad_id)
    if not s:
        raise HTTPException(404, "Scadenza non trovata")
    session.delete(s)
    session.commit()
    return {"ok": True}
