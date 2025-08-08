# Gestione Sinistri - WebApp (MVP)

MVP full-stack **FastAPI + SQLModel + Jinja2** per gestione sinistri, soggetti, documenti, comunicazioni e scadenze.
Funziona localmente senza dipendenze esterne (DB SQLite).

## Funzionalità incluse
- CRUD **Sinistri** (codice compagnia obbligatorio)
- CRUD **Soggetti** con ruoli (Cliente/Controparte/Testimone/Legale)
- **Documenti** con upload file su cartella `uploads/` e metadati collegati a Sinistro e Soggetto
- **Comunicazioni** (tipo, data, contenuto sintetico) collegate a Sinistro
- **Scadenze** con data e stato collegate a Sinistro/Soggetto
- Interfaccia server-side semplice (Jinja2) + Swagger UI per API

## Requisiti
- Python 3.10+

## Avvio rapido
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Apri: http://127.0.0.1:8000  (UI)  
Docs API: http://127.0.0.1:8000/docs

## Struttura
- `app/main.py` — bootstrap FastAPI, mount static, include router pagine e API
- `app/models.py` — modelli SQLModel & relazioni
- `app/routers/*.py` — endpoint API REST per entità
- `app/templates/*.html` — pagine HTML
- `uploads/` — file caricati
- `sinistri.db` — database SQLite creato automaticamente

## Note
- Questo è un MVP: autenticazione e ruoli non sono inclusi (si possono aggiungere JWT/Sessioni in seguito).
- Per backup, salva l'intero file `sinistri.db` e la cartella `uploads/`.