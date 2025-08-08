
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from ..database import get_session
from ..models import Coinvolgimento, CoinvolgimentoBase

router = APIRouter(prefix="/api/coinvolgimenti", tags=["Coinvolgimenti"])

@router.get("/", response_model=List[Coinvolgimento])
def list_coinvolgimenti(session: Session = Depends(get_session)):
    return session.exec(select(Coinvolgimento).order_by(Coinvolgimento.id.desc())).all()

@router.post("/", response_model=Coinvolgimento)
def create_coinvolgimento(data: CoinvolgimentoBase, session: Session = Depends(get_session)):
    c = Coinvolgimento.from_orm(data)
    session.add(c)
    session.commit()
    session.refresh(c)
    return c

@router.delete("/{cid}")
def delete_coinvolgimento(cid: int, session: Session = Depends(get_session)):
    c = session.get(Coinvolgimento, cid)
    if not c:
        raise HTTPException(404, "Coinvolgimento non trovato")
    session.delete(c)
    session.commit()
    return {"ok": True}
