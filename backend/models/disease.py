"""Symptom and disease reference models."""

from typing import Optional

from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Symptom(Base):
    __tablename__ = "symptoms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    body_system: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    severity_hint: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)


class Disease(Base):
    __tablename__ = "diseases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    icd_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    common_symptoms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    specialist: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    urgency_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    prevalence_score: Mapped[float] = mapped_column(Float, default=0.5)
