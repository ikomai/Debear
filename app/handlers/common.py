"""Start command, main-menu navigation, help, contact and cancel."""
from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app import keyboards, texts
from app.database import repository

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await repository.get_or_create_user(
        message.from_user.id, message.from_user.username, message.from_user.full_name
    )
    await message.answer(texts.WELCOME, reply_markup=keyboards.main_menu())


@router.message(Command("cancel"))
@router.message(F.text.casefold() == "cancel")
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(texts.CANCELLED, reply_markup=keyboards.main_menu())


@router.message(F.text == texts.MENU_HELP)
async def show_help(message: Message):
    await message.answer(texts.HELP)


@router.message(F.text == texts.MENU_CONTACT)
async def show_contact(message: Message):
    await message.answer(texts.CONTACT)


@router.message(F.text == texts.MENU_DOCS)
async def show_docs(message: Message):
    await message.answer(
        "📄 You can attach documents while filling in an application "
        "(step 12). Supported formats: PDF, JPEG, PNG, HEIC."
    )
