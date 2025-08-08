
import os
from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from starlette.middleware.sessions import SessionMiddleware

from .database import init_db, get_session
from .models import Sinistro, Soggetto, Documento, Comunicazione, Scadenza, Coinvolgimento
from .routers import sinistri as sinistri_api
from .routers import soggetti as soggetti_api
from .routers import documenti as documenti_api
from .routers import comunicazioni as comunicazioni_api
from .routers import scadenze as scadenze_api
from .routers import coinvolgimenti as coinvolgimenti_api

app = FastAPI(title="Gestione Sinistri - MVP Protetto")

SECRET = os.getenv("SECRET_KEY", "change-me-in-env")
app.add_middleware(SessionMiddleware, secret_key=SECRET)

app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

def auth_required(request: Request):
    if not request.session.get("auth"):
        return RedirectResponse(url="/login", status_code=303)

app.include_router(sinistri_api.router, dependencies=[Depends(auth_required)])
app.include_router(soggetti_api.router, dependencies=[Depends(auth_required)])
app.include_router(documenti_api.router, dependencies=[Depends(auth_required)])
app.include_router(comunicazioni_api.router, dependencies=[Depends(auth_required)])
app.include_router(scadenze_api.router, dependencies=[Depends(auth_required)])
app.include_router(coinvolgimenti_api.router, dependencies=[Depends(auth_required)])

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    USER = os.getenv("APP_USERNAME", "admin")
    PASS = os.getenv("APP_PASSWORD", "password")
    if username == USER and password == PASS:
        request.session["auth"] = True
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Credenziali errate"})

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

@app.get("/", response_class=HTMLResponse)
def home(request: Request, session: Session = Depends(get_session)):
    if not request.session.get("auth"):
        return RedirectResponse(url="/login", status_code=303)
    sinistri = session.exec(select(Sinistro).order_by(Sinistro.id.desc())).all()
    return templates.TemplateResponse("home.html", {"request": request, "sinistri": sinistri})

@app.get("/sinistri/new", response_class=HTMLResponse)
def form_sinistro(request: Request):
    if not request.session.get("auth"):
        return RedirectResponse(url="/login", status_code=303)
    soggetti = session = None
    return templates.TemplateResponse("sinistro_form.html", {"request": request})

@app.post("/sinistri/new")
def create_sinistro(
    request: Request,
    codice_compagnia: str = Form(...),
    data_evento: str = Form(None),
    compagnia: str = Form(None),
    termine_gestione_giorni: int = Form(60),
    liquidatore: str = Form(None),
    telefono_liquidatore: str = Form(None),
    email_liquidatore: str = Form(None),
    note: str = Form(None),
    per_lesioni: str = Form(None),
    session: Session = Depends(get_session),
):
    if not request.session.get("auth"):
        return RedirectResponse(url="/login", status_code=303)
    s = Sinistro(
        codice_compagnia=codice_compagnia,
        data_evento=data_evento or None,
        compagnia=compagnia,
        termine_gestione_giorni=termine_gestione_giorni,
        liquidatore=liquidatore,
        telefono_liquidatore=telefono_liquidatore,
        email_liquidatore=email_liquidatore,
        note=note,
        per_lesioni=True if per_lesioni == "on" else False,
    )
    session.add(s)
    session.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/sinistri/{sid}", response_class=HTMLResponse)
def sinistro_detail(sid: int, request: Request, session: Session = Depends(get_session)):
    if not request.session.get("auth"):
        return RedirectResponse(url="/login", status_code=303)
    s = session.get(Sinistro, sid)
    if not s:
        return RedirectResponse(url="/", status_code=303)
    docs = session.exec(select(Documento).where(Documento.sinistro_id == sid)).all()
    comms = session.exec(select(Comunicazione).where(Comunicazione.sinistro_id == sid)).all()
    scads = session.exec(select(Scadenza).where(Scadenza.sinistro_id == sid)).all()
    coinvolg = session.exec(select(Coinvolgimento).where(Coinvolgimento.sinistro_id == sid)).all()

    # Antifrode: per ogni legale coinvolto, controlla se in altri sinistri lo stesso legale è 'avverso' allo stesso soggetto
    warnings = []
    for c in coinvolg:
        if c.ruolo == 'legale' and c.rappresentato_id:
            legale_id = c.soggetto_id
            cliente_id = c.rappresentato_id
            # trova altri sinistri dove compaiono sia il legale che il cliente
            others = session.exec(select(Coinvolgimento).where(Coinvolgimento.soggetto_id == legale_id, Coinvolgimento.sinistro_id != sid)).all()
            for o in others:
                # nello stesso sinistro 'o.sinistro_id' compare anche il cliente?
                presenza_cliente = session.exec(select(Coinvolgimento).where(Coinvolgimento.sinistro_id == o.sinistro_id, Coinvolgimento.soggetto_id == cliente_id)).first()
                if presenza_cliente and (o.rappresentato_id is None or o.rappresentato_id != cliente_id):
                    warnings.append(f"Possibile conflitto: il legale (ID {legale_id}) risulta avverso al soggetto (ID {cliente_id}) nel sinistro ID {o.sinistro_id}.")

    return templates.TemplateResponse("sinistro_detail.html", {
        "request": request,
        "s": s, "docs": docs, "comms": comms, "scads": scads, "coinvolg": coinvolg, "warnings": warnings
    })

@app.get("/soggetti/{pid}", response_class=HTMLResponse)
def soggetto_detail(pid: int, request: Request, session: Session = Depends(get_session)):
    if not request.session.get("auth"):
        return RedirectResponse(url="/login", status_code=303)
    p = session.get(Soggetto, pid)
    if not p:
        return RedirectResponse(url="/", status_code=303)
    coinvolg = session.exec(select(Coinvolgimento).where(Coinvolgimento.soggetto_id == pid)).all()
    sinistri_ids = [c.sinistro_id for c in coinvolg]
    sinistri = session.exec(select(Sinistro).where(Sinistro.id.in_(sinistri_ids))).all() if sinistri_ids else []
    # Antifrode per soggetto: se esiste un legale che in un altro sinistro è avverso allo stesso soggetto
    warnings = []
    for c in coinvolg:
        if c.ruolo == 'legale' and c.rappresentato_id:
            # se il soggetto è un legale che rappresenta qualcuno, non ci interessa qui; controlliamo il soggetto 'pid'
            continue
        # cerca legali in quei sinistri che NON rappresentano pid
        legali_avversi = session.exec(select(Coinvolgimento).where(Coinvolgimento.sinistro_id == c.sinistro_id, Coinvolgimento.ruolo == 'legale', (Coinvolgimento.rappresentato_id.is_(None)) | (Coinvolgimento.rappresentato_id != pid))).all()
        for la in legali_avversi:
            # lo stesso legale la.soggetto_id in qualche altro sinistro rappresenta pid?
            rappresenta_pid_altrove = session.exec(select(Coinvolgimento).where(Coinvolgimento.soggetto_id == la.soggetto_id, Coinvolgimento.ruolo == 'legale', Coinvolgimento.rappresentato_id == pid, Coinvolgimento.sinistro_id != c.sinistro_id)).first()
            if rappresenta_pid_altrove:
                warnings.append(f"Possibile conflitto: il legale (ID {la.soggetto_id}) in un altro sinistro rappresenta questo soggetto ma qui appare come avverso (sinistro ID {c.sinistro_id}).")

    return templates.TemplateResponse("soggetto_detail.html", {
        "request": request, "p": p, "coinvolg": coinvolg, "sinistri": sinistri, "warnings": warnings
    })

@app.get("/scadenze/{scid}", response_class=HTMLResponse)
def scadenza_detail(scid: int, request: Request, session: Session = Depends(get_session)):
    if not request.session.get("auth"):
        return RedirectResponse(url="/login", status_code=303)
    sc = session.get(Scadenza, scid)
    if not sc:
        return RedirectResponse(url="/", status_code=303)
    sinistro = session.get(Sinistro, sc.sinistro_id) if sc.sinistro_id else None
    return templates.TemplateResponse("scadenza_detail.html", {"request": request, "sc": sc, "sinistro": sinistro})
