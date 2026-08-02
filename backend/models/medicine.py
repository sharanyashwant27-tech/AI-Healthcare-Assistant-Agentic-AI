"""Medicine and prescription models."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

if TYPE_CHECKING:
    from models.patient import Patient


class Medicine(Base):
    __tablename__ = "medicines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    generic_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    drug_class: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    common_dosage: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    contraindications: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    interactions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    side_effects: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class Prescription(Base):
    __tablename__ = "prescriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)
    doctor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("doctors.id"), nullable=True)
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    medicines_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    dosage: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    analysis_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    patient: Mapped["Patient"] = relationship("Patient", back_populates="prescriptions")
