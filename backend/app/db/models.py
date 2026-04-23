from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Boolean, DateTime, Integer, ForeignKey, func
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Topic(Base):
    __tablename__ = "topics"

    id:          Mapped[int] = mapped_column(Integer, primary_key=True)
    topic_id:    Mapped[int] = mapped_column(Integer, unique=True, index=True)
    label:       Mapped[str] = mapped_column(Text)
    keywords:    Mapped[str] = mapped_column(Text)
    paper_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_at:  Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationship back to papers
    papers: Mapped[list["Paper"]] = relationship(back_populates="topic")

class Paper(Base):
    __tablename__ = "papers"

    id:           Mapped[int]      = mapped_column(Integer, primary_key=True)
    arxiv_id:     Mapped[str]      = mapped_column(String(50), unique=True, index=True)
    title:        Mapped[str]      = mapped_column(Text)
    abstract:     Mapped[str]      = mapped_column(Text)
    summary:      Mapped[str|None] = mapped_column(Text)
    authors:      Mapped[str]      = mapped_column(Text)
    category:     Mapped[str]      = mapped_column(String(20))
    pdf_url:      Mapped[str]      = mapped_column(Text)
    arxiv_url:    Mapped[str]      = mapped_column(Text)
    published_at: Mapped[datetime] = mapped_column(DateTime)
    is_processed: Mapped[bool]     = mapped_column(Boolean, default=False)
    created_at:   Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # NEW: The foreign key linking this paper to a specific topic
    topic_id:     Mapped[int|None] = mapped_column(ForeignKey("topics.topic_id"))

    # Relationships
    entities: Mapped[list["Entity"]] = relationship(back_populates="paper", cascade="all, delete-orphan")
    topic: Mapped["Topic"] = relationship(back_populates="papers")

class Entity(Base):
    __tablename__ = "entities"

    id:          Mapped[int] = mapped_column(Integer, primary_key=True)
    paper_id:    Mapped[int] = mapped_column(ForeignKey("papers.id"), index=True)
    entity_type: Mapped[str] = mapped_column(String(30))
    value:       Mapped[str] = mapped_column(String(200))

    paper: Mapped["Paper"] = relationship(back_populates="entities")