"""Data-access helpers used by the handlers."""
from __future__ import annotations

import random
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database.base import async_session
from app.database.models import (
    Application,
    Document,
    Owner,
    Property,
    StatusHistory,
    User,
)


async def get_or_create_user(telegram_id: int, username: str | None, full_name: str | None) -> User:
    async with async_session() as session:
        user = (
            await session.scalars(select(User).where(User.telegram_id == telegram_id))
        ).first()
        if user is None:
            user = User(telegram_id=telegram_id, username=username, full_name=full_name)
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user


def _generate_number() -> str:
    return f"{random.randint(10000, 99999)}"


async def create_application(telegram_id: int, data: dict) -> Application:
    """Persist a completed questionnaire (the FSM data dict) into all tables."""
    async with async_session() as session:
        user = (
            await session.scalars(select(User).where(User.telegram_id == telegram_id))
        ).first()
        if user is None:
            user = User(
                telegram_id=telegram_id,
                username=data.get("username"),
                full_name=data.get("owner_name"),
            )
            session.add(user)
            await session.flush()

        # keep contact info on the user record up to date
        user.full_name = data.get("owner_name") or user.full_name
        user.phone = data.get("phone") or user.phone
        user.email = data.get("email") or user.email

        app = Application(
            user_id=user.id,
            number=_generate_number(),
            status="submitted",
            property_type=data.get("property_type"),
            purpose=data.get("purpose"),
            insured_sum=data.get("insured_sum"),
            term_months=int(data["term"]) if data.get("term") else None,
            has_mortgage=data.get("has_mortgage") == "yes",
            bank=data.get("bank"),
            contract_number=data.get("contract_number"),
            contract_date=data.get("contract_date"),
            debt_balance=data.get("debt_balance"),
            coverage=data.get("coverage", []),
            risks=data.get("risks", []),
            extra=data.get("extra", {}),
            consent=True,
        )
        session.add(app)
        await session.flush()

        session.add(
            Property(
                application_id=app.id,
                country=data.get("country"),
                region=data.get("region"),
                city=data.get("city"),
                street=data.get("street"),
                house=data.get("house"),
                building=data.get("building"),
                apartment=data.get("apartment"),
                postal_code=data.get("postal_code"),
                year_built=data.get("year_built"),
                floors_total=data.get("floors_total"),
                floor=data.get("floor"),
                total_area=data.get("total_area"),
                living_area=data.get("living_area"),
                wall_material=data.get("wall_material"),
                ceiling_material=data.get("ceiling_material"),
                renovation=data.get("renovation"),
                value=data.get("value"),
                cadastral_number=data.get("cadastral_number"),
            )
        )
        session.add(
            Owner(
                application_id=app.id,
                full_name=data.get("owner_name"),
                birth_date=data.get("birth_date"),
                gender=data.get("gender"),
                phone=data.get("phone"),
                email=data.get("email"),
                inn=data.get("inn"),
                passport_series=data.get("passport_series"),
                passport_number=data.get("passport_number"),
                passport_issued_by=data.get("passport_issued_by"),
                passport_issue_date=data.get("passport_issue_date"),
            )
        )
        for doc in data.get("documents", []):
            session.add(
                Document(
                    application_id=app.id,
                    doc_type=doc.get("type"),
                    file_id=doc.get("file_id"),
                    file_path=doc.get("file_path"),
                )
            )
        session.add(
            StatusHistory(
                application_id=app.id,
                old_status=None,
                new_status="submitted",
                changed_by=telegram_id,
                comment="Application submitted by client",
            )
        )
        await session.commit()
        return await get_application(app.id)


async def get_application(app_id: int) -> Application | None:
    async with async_session() as session:
        return (
            await session.scalars(
                select(Application)
                .where(Application.id == app_id)
                .options(
                    selectinload(Application.property),
                    selectinload(Application.owner),
                    selectinload(Application.documents),
                    selectinload(Application.user),
                )
            )
        ).first()


async def list_user_applications(telegram_id: int) -> list[Application]:
    async with async_session() as session:
        return list(
            await session.scalars(
                select(Application)
                .join(User)
                .where(User.telegram_id == telegram_id)
                .order_by(Application.created_at.desc())
            )
        )


async def list_all_applications(status: str | None = None, limit: int = 50) -> list[Application]:
    async with async_session() as session:
        query = select(Application).options(selectinload(Application.user))
        if status:
            query = query.where(Application.status == status)
        query = query.order_by(Application.created_at.desc()).limit(limit)
        return list(await session.scalars(query))


async def set_status(app_id: int, new_status: str, changed_by: int, comment: str | None = None):
    async with async_session() as session:
        app = await session.get(Application, app_id)
        if app is None:
            return None
        old = app.status
        app.status = new_status
        session.add(
            StatusHistory(
                application_id=app_id,
                old_status=old,
                new_status=new_status,
                changed_by=changed_by,
                comment=comment,
            )
        )
        await session.commit()
        return app
