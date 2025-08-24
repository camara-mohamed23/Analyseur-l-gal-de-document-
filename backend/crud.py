from sqlalchemy.orm import Session
from . import models

def create_document(db: Session, filename: str, path: str, summary: str | None, language: str | None):
    doc = models.Document(filename=filename, path=path, summary=summary, language=language)
    db.add(doc); db.flush()
    return doc

def add_clause(db: Session, document_id: int, title: str | None, text: str, summary: str | None, order_index:int):
    c = models.Clause(document_id=document_id, title=title, text=text, summary=summary, order_index=order_index)
    db.add(c); db.flush()
    return c

def add_entity(db: Session, document_id: int, text: str, label: str, start=None, end=None):
    e = models.Entity(document_id=document_id, text=text, label=label, start_char=start, end_char=end)
    db.add(e); db.flush()
    return e

def add_risk(db: Session, document_id: int, code: str, level: models.RiskLevel, message: str):
    r = models.Risk(document_id=document_id, code=code, level=level, message=message)
    db.add(r); db.flush()
    return r

def get_document(db: Session, doc_id: int):
    return db.query(models.Document).filter(models.Document.id==doc_id).first()

def list_documents(db: Session, limit=50, offset=0):
    return db.query(models.Document).order_by(models.Document.id.desc()).offset(offset).limit(limit).all()
