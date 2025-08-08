
from typing import Optional
from datetime import date
from sqlmodel import SQLModel, Field, Relationship

class SinistroBase(SQLModel):
    codice_compagnia: str = Field(index=True, description="Numero sinistro assegnato dalla compagnia")
    data_evento: Optional[date] = Field(default=None)
    compagnia: Optional[str] = None
    termine_gestione_giorni: Optional[int] = Field(default=60, description="30/60/90")
    liquidatore: Optional[str] = None
    telefono_liquidatore: Optional[str] = None
    email_liquidatore: Optional[str] = None
    note: Optional[str] = None
    per_lesioni: Optional[bool] = Field(default=False, description="Se true, mostra suggerimenti documentazione medica")

class Sinistro(SinistroBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    documenti: list['Documento'] = Relationship(back_populates='sinistro')
    comunicazioni: list['Comunicazione'] = Relationship(back_populates='sinistro')
    scadenze: list['Scadenza'] = Relationship(back_populates='sinistro')
    coinvolgimenti: list['Coinvolgimento'] = Relationship(back_populates='sinistro')

class SoggettoBase(SQLModel):
    nome: str
    cognome: str
    ruolo: str  # Cliente/Controparte/Testimone/Legale
    codice_fiscale: Optional[str] = Field(default=None, index=True)
    telefono: Optional[str] = None
    email: Optional[str] = None

class Soggetto(SoggettoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    documenti: list['Documento'] = Relationship(back_populates='soggetto')
    scadenze: list['Scadenza'] = Relationship(back_populates='soggetto')
    coinvolgimenti: list['Coinvolgimento'] = Relationship(back_populates='soggetto')

class DocumentoBase(SQLModel):
    tipo: str
    data: Optional[date] = None
    descrizione: Optional[str] = None
    file_path: Optional[str] = Field(default=None, description='Percorso locale del file salvato')

class Documento(DocumentoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sinistro_id: Optional[int] = Field(default=None, foreign_key='sinistro.id')
    soggetto_id: Optional[int] = Field(default=None, foreign_key='soggetto.id')
    sinistro: Optional['Sinistro'] = Relationship(back_populates='documenti')
    soggetto: Optional['Soggetto'] = Relationship(back_populates='documenti')

class ComunicazioneBase(SQLModel):
    data: Optional[date] = None
    tipo: Optional[str] = Field(default='Email')  # PEC / Email / Verbale
    contenuto_sintetico: Optional[str] = None
    mitt_dest: Optional[str] = Field(default=None, description='Mittente / Destinatario')
    allegato_path: Optional[str] = None
    sinistro_id: Optional[int] = Field(default=None, foreign_key='sinistro.id')

class Comunicazione(ComunicazioneBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sinistro: Optional['Sinistro'] = Relationship(back_populates='comunicazioni')

class ScadenzaBase(SQLModel):
    data: Optional[date] = None
    descrizione: Optional[str] = None
    tipo: Optional[str] = Field(default='Visita')  # Visita / Chiamata / Perizia
    stato: Optional[str] = Field(default='In attesa')
    sinistro_id: Optional[int] = Field(default=None, foreign_key='sinistro.id')
    soggetto_id: Optional[int] = Field(default=None, foreign_key='soggetto.id')

class Scadenza(ScadenzaBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sinistro: Optional['Sinistro'] = Relationship(back_populates='scadenze')
    soggetto: Optional['Soggetto'] = Relationship(back_populates='scadenze')

class CoinvolgimentoBase(SQLModel):
    ruolo: str  # attore/convenuto/testimone/legale
    sinistro_id: int = Field(foreign_key='sinistro.id')
    soggetto_id: int = Field(foreign_key='soggetto.id')
    rappresentato_id: Optional[int] = Field(default=None, foreign_key='soggetto.id', description='Solo per legale: ID del soggetto rappresentato')

class Coinvolgimento(CoinvolgimentoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sinistro: Optional['Sinistro'] = Relationship(back_populates='coinvolgimenti')
    soggetto: Optional['Soggetto'] = Relationship(back_populates='coinvolgimenti')
