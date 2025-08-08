from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session, select
from typing import List, Optional
from pathlib import Path
from datetime import date
from ..database import get_session
from ..models import Documento, DocumentoBase

router = APIRouter(prefix="/api/documenti", tags=["Documenti"])
UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/", response_model=List[Documento])
def list_documenti(session: Session = Depends(get_session)):
    return session.exec(select(Documento).order_by(Documento.id.desc())).all()

@router.post("/", response_model=Documento)
async def create_documento(
    tipo: str = Form(...),
    descrizione: Optional[str] = Form(None),
    data: Optional[str] = Form(None),
    sinistro_id: Optional[int] = Form(None),
    soggetto_id: Optional[int] = Form(None),
    file: UploadFile = File(None),
    session: Session = Depends(get_session),
):
    file_path = None
    if file is not None:
        dest = UPLOAD_DIR / file.filename
        content = await file.read()
        dest.write_bytes(content)
        file_path = str(dest)

    d = Documento(
        tipo=tipo,
        descrizione=descrizione,
        data=date.fromisoformat(data) if data else None,
        sinistro_id=sinistro_id,
        soggetto_id=soggetto_id,
        file_path=file_path,
    )
    session.add(d)
    session.commit()
    session.refresh(d)
    return d

@router.delete("/{doc_id}")
def delete_documento(doc_id: int, session: Session = Depends(get_session)):
    d = session.get(Documento, doc_id)
    if not d:
        raise HTTPException(404, "Documento non trovato")
    session.delete(d)
    session.commit()
    return {"ok": True}