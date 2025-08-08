from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from ..database import get_session
from ..models import Comunicazione, ComunicazioneBase

router = APIRouter(prefix="/api/comunicazioni", tags=["Comunicazioni"])

@router.get("/", response_model=List[Comunicazione])
def list_comunicazioni(session: Session = Depends(get_session)):
    return session.exec(select(Comunicazione).order_by(Comunicazione.id.desc())).all()

@router.post("/", response_model=Comunicazione)
def create_comunicazione(data: ComunicazioneBase, session: Session = Depends(get_session)):
    c = Comunicazione.from_orm(data)
    session.add(c)
    session.commit()
    session.refresh(c)
    return c

@router.delete("/{com_id}")
def delete_comunicazione(com_id: int, session: Session = Depends(get_session)):
    c = session.get(Comunicazione, com_id)
    if not c:
        raise HTTPException(404, "Comunicazione non trovata")
    session.delete(c)
    session.commit()
    return {"ok": True}
