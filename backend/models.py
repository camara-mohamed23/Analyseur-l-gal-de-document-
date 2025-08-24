from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum

class RiskLevel(enum.Enum):
    low="low"; medium="medium"; high="high"

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    path = Column(String(500), nullable=False)
    language = Column(String(10), nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    clauses = relationship("Clause", back_populates="document", cascade="all, delete-orphan")
    entities = relationship("Entity", back_populates="document", cascade="all, delete-orphan")
    risks    = relationship("Risk",   back_populates="document", cascade="all, delete-orphan")

class Clause(Base):
    __tablename__ = "clauses"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), index=True)
    title = Column(String(255), nullable=True)
    text = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    order_index = Column(Integer, default=0)

    document = relationship("Document", back_populates="clauses")

class Entity(Base):
    __tablename__ = "entities"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), index=True)
    text = Column(String(500), nullable=False)
    label = Column(String(50), nullable=False)
    start_char = Column(Integer, nullable=True)
    end_char = Column(Integer, nullable=True)

    document = relationship("Document", back_populates="entities")

class Risk(Base):
    __tablename__ = "risks"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), index=True)
    code = Column(String(50), nullable=False)
    level = Column(Enum(RiskLevel), nullable=False)
    message = Column(String(500), nullable=False)

    document = relationship("Document", back_populates="risks")
