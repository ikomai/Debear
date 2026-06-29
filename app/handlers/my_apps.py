"""Personal cabinet — the client's own applications and their status."""
from aiogram import F, Router
from aiogram.types import Message

from app import texts
from app.database import repository

router = Router()


@router.message(F.text == texts.MENU_MY_APPS)
async def my_applications(message: Message):
    apps = await repository.list_user_applications(message.from_user.id)
    if not apps:
        await message.answer(texts.NO_APPS)
        return

    lines = ["📋 <b>Your applications</b>\n"]
    for app in apps:
        status = texts.STATUS_LABELS.get(app.status, app.status)
        sum_str = f"{float(app.insured_sum):,.0f}" if app.insured_sum else "—"
        lines.append(
            f"• <b>#{app.number}</b> — {status}\n"
            f"   {texts.label_of(texts.PROPERTY_TYPES, app.property_type)} · "
            f"sum {sum_str} · {app.created_at:%d.%m.%Y}"
        )
    await message.answer("\n".join(lines))
