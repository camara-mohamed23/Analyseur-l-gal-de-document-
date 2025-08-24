import os, shutil
from fastapi import FastAPI, UploadFile, File, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .pipeline import analyze, UPLOAD_DIR

from typing import List

from .database import Base, engine, get_db
from . import models, crud, schemas
from .pipeline import analyze, UPLOAD_DIR
from .search import ClauseIndex

# Création des tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Analyseur de document")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# Index recherche
INDEX = ClauseIndex(index_dir=os.getenv("INDEX_DIR", "backend/indexes"))
INDEX.load()

def rebuild_index(db: Session):
    rows = db.query(models.Clause).all()
    meta = [(c.document_id, c.id, c.title or "Clause", c.text or "") for c in rows]
    if meta:
        INDEX.build(meta)

# Enum coercion (LOW/MEDIUM/HIGH, peu importe casse/valeur)
from .models import RiskLevel as DBRiskLevel
def _coerce_level(x):
    if x is None:
        return DBRiskLevel.LOW
    sx = str(x).upper()
    by_name = {m.name.upper(): m for m in DBRiskLevel}
    if sx in by_name: return by_name[sx]
    by_value = {str(m.value).upper(): m for m in DBRiskLevel}
    return by_value.get(sx, DBRiskLevel.LOW)

# ---------- Routes ----------
@app.post("/upload", response_model=schemas.DocumentOut)
async def upload(file: UploadFile = File(...), db: Session = Depends(get_db)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    path = os.path.join(UPLOAD_DIR, file.filename)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    language, summary, clauses, entities, risks = analyze(path)
    doc = crud.create_document(db, filename=file.filename, path=path, summary=summary, language=language)

    for c in clauses:
        crud.add_clause(db, doc.id, c.get("title"), c["text"], c.get("summary"), c.get("order_index"))
    for e in entities.get("ents", []):
        crud.add_entity(db, doc.id, e.get("text", ""), e.get("label"), e.get("start"), e.get("end"))
    for r in risks:
        crud.add_risk(db, doc.id, r.get("code", "RISK"), _coerce_level(r.get("level")), r.get("message"))

    db.commit()
    rebuild_index(db)
    db.refresh(doc)
    return doc

@app.get("/documents", response_model=List[schemas.DocumentOut])
def list_docs(limit:int=50, offset:int=0, db: Session=Depends(get_db)):
    return crud.list_documents(db, limit=limit, offset=offset)

@app.get("/documents/{doc_id}", response_model=schemas.DocumentOut)
def get_doc(doc_id:int, db: Session=Depends(get_db)):
    doc = crud.get_document(db, doc_id)
    if not doc:
        raise HTTPException(404, "Document introuvable")
    return doc

@app.get("/search", response_model=List[dict])
def search(q: str = Query(..., min_length=2), k: int = 5, db: Session = Depends(get_db)):
    hits = INDEX.search(q, k=k)
    return hits

@app.post("/reindex")
def reindex(db: Session = Depends(get_db)):
    rebuild_index(db)
    return {"status": "ok"}
