"""Minimal admin panel: list applications and change their status.

Access is restricted to the Telegram IDs listed in ADMIN_IDS (.env).
A full admin panel (search, filters, Excel/CSV export, manager assignment,
comments) is part of the larger spec and is intentionally out of MVP scope.
"""
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app import keyboards, texts
from app.config import settings
from app.database import repository

router = Router()


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not settings.is_admin(message.from_user.id):
        await message.answer("⛔ You don't have access to the admin panel.")
        return

    apps = await repository.list_all_applications(limit=20)
    if not apps:
        await message.answer("No applications yet.")
        return

    await message.answer(f"🛠 <b>Admin panel</b> — last {len(apps)} applications:")
    for app in apps:
        status = texts.STATUS_LABELS.get(app.status, app.status)
        client = app.user.full_name or app.user.username or app.user.telegram_id
        await message.answer(
            f"<b>#{app.number}</b> — {status}\n"
            f"Client: {client}\n"
            f"Type: {texts.label_of(texts.PROPERTY_TYPES, app.property_type)} · "
            f"Sum: {float(app.insured_sum):,.0f}\n"
            f"Date: {app.created_at:%d.%m.%Y %H:%M}",
            reply_markup=keyboards.admin_app_kb(app.id),
        )


@router.callback_query(F.data.startswith("setstatus:"))
async def change_status(cb: CallbackQuery):
    if not settings.is_admin(cb.from_user.id):
        await cb.answer("No access", show_alert=True)
        return

    _, app_id, new_status = cb.data.split(":")
    app = await repository.set_status(int(app_id), new_status, cb.from_user.id)
    if app is None:
        await cb.answer("Application not found", show_alert=True)
        return

    label = texts.STATUS_LABELS.get(new_status, new_status)
    await cb.message.edit_text(
        cb.message.html_text + f"\n\n➡️ Status changed to: <b>{label}</b>"
    )
    await cb.answer(f"Status: {label}")

    # Notify the client about the status change.
    try:
        full = await repository.get_application(int(app_id))
        await cb.bot.send_message(
            full.user.telegram_id,
            f"🔔 Your application <b>#{full.number}</b> status changed to: <b>{label}</b>",
        )
    except Exception:
        pass
