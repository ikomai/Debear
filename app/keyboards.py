"""Reusable keyboard builders."""
from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app import texts


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=texts.MENU_NEW)],
            [KeyboardButton(text=texts.MENU_MY_APPS), KeyboardButton(text=texts.MENU_DOCS)],
            [KeyboardButton(text=texts.MENU_HELP), KeyboardButton(text=texts.MENU_CONTACT)],
        ],
        resize_keyboard=True,
    )


def begin_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=texts.BTN_BEGIN, callback_data="begin")]]
    )


def options_kb(options: list[tuple[str, str]], prefix: str, columns: int = 1) -> InlineKeyboardMarkup:
    """Single-choice keyboard: callback_data = '<prefix>:<value>'."""
    builder = InlineKeyboardBuilder()
    for value, label in options:
        builder.button(text=label, callback_data=f"{prefix}:{value}")
    builder.adjust(columns)
    return builder.as_markup()


def multi_kb(
    options: list[tuple[str, str]], prefix: str, selected: list[str], done_cb: str
) -> InlineKeyboardMarkup:
    """Multi-select keyboard with a check mark on chosen items plus a Next button."""
    builder = InlineKeyboardBuilder()
    for value, label in options:
        mark = "☑️ " if value in selected else "⬜ "
        builder.button(text=f"{mark}{label}", callback_data=f"{prefix}:{value}")
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="➡️ Next", callback_data=done_cb))
    return builder.as_markup()


def suggestions_kb(field: str, suggestions: list[str], allow_keep: bool = True) -> InlineKeyboardMarkup:
    """Buttons offering 'did you mean' alternatives for a mistyped value.

    callback_data = 'sugg:<field>:<index>'  (or ':keep' to use the typed value).
    """
    builder = InlineKeyboardBuilder()
    for i, text in enumerate(suggestions):
        builder.button(text=text[:60], callback_data=f"sugg:{field}:{i}")
    if allow_keep:
        builder.button(text="✅ Keep my input", callback_data=f"sugg:{field}:keep")
    builder.adjust(1)
    return builder.as_markup()


def docs_done_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=texts.BTN_DOCS_DONE, callback_data="docs_done")]]
    )


def review_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=texts.BTN_EDIT, callback_data="review_edit"),
                InlineKeyboardButton(text=texts.BTN_SUBMIT, callback_data="review_submit"),
            ]
        ]
    )


def consent_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=texts.BTN_CONSENT, callback_data="consent_ok")]]
    )


# ─────────── Admin ───────────
def admin_app_kb(app_id: int) -> InlineKeyboardMarkup:
    """Status-change buttons shown to an admin under each application."""
    from app.texts import STATUS_LABELS

    builder = InlineKeyboardBuilder()
    for status in ["in_review", "awaiting_docs", "approved", "rejected", "policy_issued", "closed"]:
        builder.button(text=STATUS_LABELS[status], callback_data=f"setstatus:{app_id}:{status}")
    builder.adjust(2)
    return builder.as_markup()
