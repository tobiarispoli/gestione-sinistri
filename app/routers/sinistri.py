from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from ..database import get_session
from ..models import Sinistro, SinistroBase

router = APIRouter(prefix="/api/sinistri", tags=["Sinistri"])

@router.get("/", response_model=List[Sinistro])
def list_sinistri(session: Session = Depends(get_session)):
    return session.exec(select(Sinistro).order_by(Sinistro.id.desc())).all()

@router.post("/", response_model=Sinistro)
def create_sinistro(data: SinistroBase, session: Session = Depends(get_session)):
    s = Sinistro.from_orm(data)
    session.add(s)
    session.commit()
    session.refresh(s)
    return s

@router.get("/{sinistro_id}", response_model=Sinistro)
def get_sinistro(sinistro_id: int, session: Session = Depends(get_session)):
    s = session.get(Sinistro, sinistro_id)
    if not s:
        raise HTTPException(404, "Sinistro non trovato")
    return s

@router.put("/{sinistro_id}", response_model=Sinistro)
def update_sinistro(sinistro_id: int, data: SinistroBase, session: Session = Depends(get_session)):
    s = session.get(Sinistro, sinistro_id)
    if not s:
        raise HTTPException(404, "Sinistro non trovato")
    for k, v in data.dict().items():
        setattr(s, k, v)
    session.add(s)
    session.commit()
    session.refresh(s)
    return s

@router.delete("/{sinistro_id}")
def delete_sinistro(sinistro_id: int, session: Session = Depends(get_session)):
    s = session.get(Sinistro, sinistro_id)
    if not s:
        raise HTTPException(404, "Sinistro non trovato")
    session.delete(s)
    session.commit()
    return {"ok": True}