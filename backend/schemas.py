from pydantic import BaseModel
from typing import List, Optional

class ClauseOut(BaseModel):
    id: int
    title: Optional[str]
    text: str
    summary: Optional[str]
    order_index: int
    class Config: orm_mode=True

class EntityOut(BaseModel):
    id: int
    text: str
    label: str
    start_char: int | None = None
    end_char: int | None = None
    class Config: orm_mode=True

class RiskOut(BaseModel):
    id: int
    code: str
    level: str
    message: str
    class Config: orm_mode=True

class DocumentOut(BaseModel):
    id: int
    filename: str
    language: str | None = None
    summary: str | None = None
    clauses: List[ClauseOut] = []
    entities: List[EntityOut] = []
    risks: List[RiskOut] = []
    class Config: orm_mode=True

class SearchHit(BaseModel):
    document_id: int
    clause_id: int
    title: str | None = None
    snippet: str
    score: float
