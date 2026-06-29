"""ORM models mirroring the data structure from the technical specification."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(64))
    full_name: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(32))
    email: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(16), default="client")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    applications: Mapped[list["Application"]] = relationship(back_populates="user")


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    number: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(32), default="submitted")

    property_type: Mapped[str | None] = mapped_column(String(32))
    purpose: Mapped[str | None] = mapped_column(String(32))
    insured_sum: Mapped[float | None] = mapped_column(Numeric(15, 2))
    term_months: Mapped[int | None] = mapped_column()

    # Mortgage
    has_mortgage: Mapped[bool] = mapped_column(default=False)
    bank: Mapped[str | None] = mapped_column(String(255))
    contract_number: Mapped[str | None] = mapped_column(String(64))
    contract_date: Mapped[str | None] = mapped_column(String(32))
    debt_balance: Mapped[str | None] = mapped_column(String(64))

    # Multi-select & extra answers stored as JSON (portable across SQLite/MySQL)
    coverage: Mapped[list | None] = mapped_column(JSON, default=list)
    risks: Mapped[list | None] = mapped_column(JSON, default=list)
    extra: Mapped[dict | None] = mapped_column(JSON, default=dict)

    consent: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="applications")
    property: Mapped["Property"] = relationship(
        back_populates="application", uselist=False, cascade="all, delete-orphan"
    )
    owner: Mapped["Owner"] = relationship(
        back_populates="application", uselist=False, cascade="all, delete-orphan"
    )
    documents: Mapped[list["Document"]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )
    history: Mapped[list["StatusHistory"]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )


class Property(Base):
    __tablename__ = "property"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"))

    country: Mapped[str | None] = mapped_column(String(128))
    region: Mapped[str | None] = mapped_column(String(128))
    city: Mapped[str | None] = mapped_column(String(128))
    street: Mapped[str | None] = mapped_column(String(255))
    house: Mapped[str | None] = mapped_column(String(32))
    building: Mapped[str | None] = mapped_column(String(32))
    apartment: Mapped[str | None] = mapped_column(String(32))
    postal_code: Mapped[str | None] = mapped_column(String(32))

    year_built: Mapped[str | None] = mapped_column(String(16))
    floors_total: Mapped[str | None] = mapped_column(String(16))
    floor: Mapped[str | None] = mapped_column(String(16))
    total_area: Mapped[str | None] = mapped_column(String(32))
    living_area: Mapped[str | None] = mapped_column(String(32))
    wall_material: Mapped[str | None] = mapped_column(String(128))
    ceiling_material: Mapped[str | None] = mapped_column(String(128))
    renovation: Mapped[str | None] = mapped_column(String(32))
    value: Mapped[str | None] = mapped_column(String(64))
    cadastral_number: Mapped[str | None] = mapped_column(String(64))

    application: Mapped["Application"] = relationship(back_populates="property")

    @property
    def full_address(self) -> str:
        parts = [
            self.postal_code,
            self.country,
            self.region,
            self.city,
            self.street,
            self.house and f"h. {self.house}",
            self.building and self.building != "-" and f"bld. {self.building}",
            self.apartment and self.apartment != "-" and f"apt. {self.apartment}",
        ]
        return ", ".join(p for p in parts if p)


class Owner(Base):
    __tablename__ = "owners"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"))

    full_name: Mapped[str | None] = mapped_column(String(255))
    birth_date: Mapped[str | None] = mapped_column(String(32))
    gender: Mapped[str | None] = mapped_column(String(16))
    phone: Mapped[str | None] = mapped_column(String(32))
    email: Mapped[str | None] = mapped_column(String(255))
    inn: Mapped[str | None] = mapped_column(String(32))
    passport_series: Mapped[str | None] = mapped_column(String(16))
    passport_number: Mapped[str | None] = mapped_column(String(16))
    passport_issued_by: Mapped[str | None] = mapped_column(Text)
    passport_issue_date: Mapped[str | None] = mapped_column(String(32))

    application: Mapped["Application"] = relationship(back_populates="owner")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"))
    doc_type: Mapped[str | None] = mapped_column(String(64))
    file_id: Mapped[str | None] = mapped_column(String(255))  # Telegram file_id
    file_path: Mapped[str | None] = mapped_column(String(512))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    application: Mapped["Application"] = relationship(back_populates="documents")


class StatusHistory(Base):
    __tablename__ = "history"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"))
    old_status: Mapped[str | None] = mapped_column(String(32))
    new_status: Mapped[str | None] = mapped_column(String(32))
    changed_by: Mapped[int | None] = mapped_column(BigInteger)
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    application: Mapped["Application"] = relationship(back_populates="history")
