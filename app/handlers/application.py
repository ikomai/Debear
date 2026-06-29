"""The step-by-step insurance application questionnaire (FSM)."""
from __future__ import annotations

import time
from pathlib import Path

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message

from app import keyboards, texts
from app.config import settings
from app.database import repository
from app.services import integrations, validation
from app.services.pdf import generate_pdf
from app.states import ApplicationForm

router = Router()


# ─────────────────────── entry ───────────────────────
@router.message(F.text == texts.MENU_NEW)
async def start_application(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(texts.WELCOME, reply_markup=keyboards.begin_kb())


@router.callback_query(F.data == "begin")
async def on_begin(cb: CallbackQuery, state: FSMContext):
    await state.set_state(ApplicationForm.property_type)
    await cb.message.edit_text(
        texts.ASK_PROPERTY_TYPE,
        reply_markup=keyboards.options_kb(texts.PROPERTY_TYPES, "ptype"),
    )
    await cb.answer()


# ─────────────────────── step 1-2: single-choice buttons ───────────────────────
@router.callback_query(ApplicationForm.property_type, F.data.startswith("ptype:"))
async def set_property_type(cb: CallbackQuery, state: FSMContext):
    await state.update_data(property_type=cb.data.split(":", 1)[1])
    await state.set_state(ApplicationForm.purpose)
    await cb.message.edit_text(
        texts.ASK_PURPOSE, reply_markup=keyboards.options_kb(texts.PURPOSES, "purpose")
    )
    await cb.answer()


@router.callback_query(ApplicationForm.purpose, F.data.startswith("purpose:"))
async def set_purpose(cb: CallbackQuery, state: FSMContext):
    await state.update_data(purpose=cb.data.split(":", 1)[1])
    await state.set_state(ApplicationForm.country)
    await cb.message.edit_text(texts.ASK_COUNTRY)
    await cb.answer()


# ─────────────────────── step 3-5: linear text questions ───────────────────────
# Ordered pipeline of plain-text states. Each entry: (state, field key it stores).
TEXT_PIPELINE: list[tuple] = [
    (ApplicationForm.country, "country"),
    (ApplicationForm.region, "region"),
    (ApplicationForm.city, "city"),
    (ApplicationForm.street, "street"),
    (ApplicationForm.house, "house"),
    (ApplicationForm.building, "building"),
    (ApplicationForm.apartment, "apartment"),
    (ApplicationForm.postal_code, "postal_code"),
    (ApplicationForm.year_built, "year_built"),
    (ApplicationForm.floors_total, "floors_total"),
    (ApplicationForm.floor, "floor"),
    (ApplicationForm.total_area, "total_area"),
    (ApplicationForm.living_area, "living_area"),
    (ApplicationForm.wall_material, "wall_material"),
    (ApplicationForm.ceiling_material, "ceiling_material"),  # -> branch: renovation
    (ApplicationForm.value, "value"),
    (ApplicationForm.cadastral_number, "cadastral_number"),
    (ApplicationForm.owner_name, "owner_name"),
    (ApplicationForm.birth_date, "birth_date"),  # -> branch: gender
    (ApplicationForm.phone, "phone"),
    (ApplicationForm.email, "email"),
    (ApplicationForm.inn, "inn"),
    (ApplicationForm.passport_series, "passport_series"),
    (ApplicationForm.passport_number, "passport_number"),
    (ApplicationForm.passport_issued_by, "passport_issued_by"),
    (ApplicationForm.passport_issue_date, "passport_issue_date"),  # -> branch: mortgage
]

# Prompt shown when entering each text state.
PROMPT = {
    ApplicationForm.country: texts.ASK_COUNTRY,
    ApplicationForm.region: texts.ASK_REGION,
    ApplicationForm.city: texts.ASK_CITY,
    ApplicationForm.street: texts.ASK_STREET,
    ApplicationForm.house: texts.ASK_HOUSE,
    ApplicationForm.building: texts.ASK_BUILDING,
    ApplicationForm.apartment: texts.ASK_APARTMENT,
    ApplicationForm.postal_code: texts.ASK_POSTAL,
    ApplicationForm.year_built: texts.ASK_YEAR_BUILT,
    ApplicationForm.floors_total: texts.ASK_FLOORS_TOTAL,
    ApplicationForm.floor: texts.ASK_FLOOR,
    ApplicationForm.total_area: texts.ASK_TOTAL_AREA,
    ApplicationForm.living_area: texts.ASK_LIVING_AREA,
    ApplicationForm.wall_material: texts.ASK_WALL_MATERIAL,
    ApplicationForm.ceiling_material: texts.ASK_CEILING_MATERIAL,
    ApplicationForm.value: texts.ASK_VALUE,
    ApplicationForm.cadastral_number: texts.ASK_CADASTRAL,
    ApplicationForm.owner_name: texts.ASK_OWNER_NAME,
    ApplicationForm.birth_date: texts.ASK_BIRTH_DATE,
    ApplicationForm.phone: texts.ASK_PHONE,
    ApplicationForm.email: texts.ASK_EMAIL,
    ApplicationForm.inn: texts.ASK_INN,
    ApplicationForm.passport_series: texts.ASK_PASSPORT_SERIES,
    ApplicationForm.passport_number: texts.ASK_PASSPORT_NUMBER,
    ApplicationForm.passport_issued_by: texts.ASK_PASSPORT_ISSUED,
    ApplicationForm.passport_issue_date: texts.ASK_PASSPORT_DATE,
}

# After these fields we jump to a button step instead of the next text question.
_BRANCH_FIELDS = {"ceiling_material", "birth_date", "passport_issue_date"}

_TEXT_STATES = [st for st, _ in TEXT_PIPELINE]
_INDEX_BY_STATE = {st.state: i for i, (st, _) in enumerate(TEXT_PIPELINE)}
_INDEX_BY_FIELD = {fld: i for i, (_, fld) in enumerate(TEXT_PIPELINE)}

# Per-field "reality"/format checks. Each is async (value, fsm_data) -> ValidationResult.
VALIDATORS = {
    "country": validation.validate_country,
    "city": validation.validate_city,
    "street": validation.validate_street,
    "email": validation.validate_email,
    "phone": validation.validate_phone,
    "birth_date": validation.validate_date,
    "passport_issue_date": validation.validate_date,
    "year_built": validation.validate_year,
    "total_area": validation.validate_positive_number,
    "living_area": validation.validate_positive_number,
    "value": validation.validate_positive_number,
}
# Fields verified online — the user may keep their input if the geocoder
# has no match. Format checks (everything else) must be corrected.
_NETWORK_FIELDS = {"city", "street"}


async def _advance(field: str, state: FSMContext, msg: Message):
    """Move to the next step after `field` has been stored."""
    if field == "ceiling_material":
        await state.set_state(ApplicationForm.renovation)
        await msg.answer(
            texts.ASK_RENOVATION, reply_markup=keyboards.options_kb(texts.RENOVATION, "renov")
        )
        return
    if field == "birth_date":
        await state.set_state(ApplicationForm.gender)
        await msg.answer(
            texts.ASK_GENDER, reply_markup=keyboards.options_kb(texts.GENDERS, "gender", columns=2)
        )
        return
    if field == "passport_issue_date":
        await state.set_state(ApplicationForm.has_mortgage)
        await msg.answer(
            texts.ASK_MORTGAGE, reply_markup=keyboards.options_kb(texts.YES_NO, "mortgage", columns=2)
        )
        return
    next_state, _ = TEXT_PIPELINE[_INDEX_BY_FIELD[field] + 1]
    await state.set_state(next_state)
    await msg.answer(PROMPT[next_state])


@router.message(StateFilter(*_TEXT_STATES), F.text)
async def collect_text(message: Message, state: FSMContext):
    current = await state.get_state()
    _, field = TEXT_PIPELINE[_INDEX_BY_STATE[current]]
    value = message.text.strip()

    validator = VALIDATORS.get(field)
    if validator:
        if field in _NETWORK_FIELDS:
            await message.bot.send_chat_action(message.chat.id, "typing")
        result = await validator(value, await state.get_data())
        if not result.ok:
            await state.update_data(
                **{f"_sugg_{field}": result.suggestions, f"_typed_{field}": value}
            )
            await message.answer(
                result.message,
                reply_markup=keyboards.suggestions_kb(
                    field, result.suggestions, allow_keep=field in _NETWORK_FIELDS
                ),
            )
            return
        value = result.value or value

    await state.update_data(**{field: value})
    await _advance(field, state, message)


@router.callback_query(F.data.startswith("sugg:"))
async def on_suggestion(cb: CallbackQuery, state: FSMContext):
    _, field, choice = cb.data.split(":", 2)
    data = await state.get_data()
    if choice == "keep":
        value = data.get(f"_typed_{field}", "")
    else:
        suggestions = data.get(f"_sugg_{field}", [])
        value = suggestions[int(choice)] if choice.isdigit() and int(choice) < len(suggestions) else ""
    await state.update_data(**{field: value})
    await cb.message.edit_text(f"✓ {field.replace('_', ' ').title()}: {value}")
    await _advance(field, state, cb.message)
    await cb.answer()


# renovation (button) -> value (text)
@router.callback_query(ApplicationForm.renovation, F.data.startswith("renov:"))
async def set_renovation(cb: CallbackQuery, state: FSMContext):
    await state.update_data(renovation=cb.data.split(":", 1)[1])
    await state.set_state(ApplicationForm.value)
    await cb.message.edit_text(texts.ASK_VALUE)
    await cb.answer()


# gender (button) -> phone (text)
@router.callback_query(ApplicationForm.gender, F.data.startswith("gender:"))
async def set_gender(cb: CallbackQuery, state: FSMContext):
    await state.update_data(gender=cb.data.split(":", 1)[1])
    await state.set_state(ApplicationForm.phone)
    await cb.message.edit_text(texts.ASK_PHONE)
    await cb.answer()


# ─────────────────────── step 6: mortgage ───────────────────────
@router.callback_query(ApplicationForm.has_mortgage, F.data.startswith("mortgage:"))
async def set_mortgage(cb: CallbackQuery, state: FSMContext):
    answer = cb.data.split(":", 1)[1]
    await state.update_data(has_mortgage=answer)
    if answer == "yes":
        await state.set_state(ApplicationForm.bank)
        await cb.message.edit_text(texts.ASK_BANK)
    else:
        await cb.message.edit_text("No mortgage — continuing.")
        await _go_to_coverage(cb.message, state)
    await cb.answer()


@router.message(ApplicationForm.bank, F.text)
async def set_bank(message: Message, state: FSMContext):
    await state.update_data(bank=message.text.strip())
    await state.set_state(ApplicationForm.contract_number)
    await message.answer(texts.ASK_CONTRACT_NUMBER)


@router.message(ApplicationForm.contract_number, F.text)
async def set_contract_number(message: Message, state: FSMContext):
    await state.update_data(contract_number=message.text.strip())
    await state.set_state(ApplicationForm.contract_date)
    await message.answer(texts.ASK_CONTRACT_DATE)


@router.message(ApplicationForm.contract_date, F.text)
async def set_contract_date(message: Message, state: FSMContext):
    await state.update_data(contract_date=message.text.strip())
    await state.set_state(ApplicationForm.debt_balance)
    await message.answer(texts.ASK_DEBT)


@router.message(ApplicationForm.debt_balance, F.text)
async def set_debt(message: Message, state: FSMContext):
    await state.update_data(debt_balance=message.text.strip())
    await _go_to_coverage(message, state)


# ─────────────────────── step 7-8: multi-select ───────────────────────
async def _go_to_coverage(message: Message, state: FSMContext):
    await state.update_data(coverage=[])
    await state.set_state(ApplicationForm.coverage)
    await message.answer(
        texts.ASK_COVERAGE,
        reply_markup=keyboards.multi_kb(texts.COVERAGE_OBJECTS, "cov", [], "cov_done"),
    )


def _toggle(selected: list[str], value: str) -> list[str]:
    selected = list(selected)
    if value in selected:
        selected.remove(value)
    else:
        selected.append(value)
    return selected


@router.callback_query(ApplicationForm.coverage, F.data.startswith("cov:"))
async def toggle_coverage(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = _toggle(data.get("coverage", []), cb.data.split(":", 1)[1])
    await state.update_data(coverage=selected)
    await cb.message.edit_reply_markup(
        reply_markup=keyboards.multi_kb(texts.COVERAGE_OBJECTS, "cov", selected, "cov_done")
    )
    await cb.answer()


@router.callback_query(ApplicationForm.coverage, F.data == "cov_done")
async def coverage_done(cb: CallbackQuery, state: FSMContext):
    await state.update_data(risks=[])
    await state.set_state(ApplicationForm.risks)
    await cb.message.edit_text(
        texts.ASK_RISKS, reply_markup=keyboards.multi_kb(texts.RISKS, "risk", [], "risk_done")
    )
    await cb.answer()


@router.callback_query(ApplicationForm.risks, F.data.startswith("risk:"))
async def toggle_risk(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = _toggle(data.get("risks", []), cb.data.split(":", 1)[1])
    await state.update_data(risks=selected)
    await cb.message.edit_reply_markup(
        reply_markup=keyboards.multi_kb(texts.RISKS, "risk", selected, "risk_done")
    )
    await cb.answer()


@router.callback_query(ApplicationForm.risks, F.data == "risk_done")
async def risks_done(cb: CallbackQuery, state: FSMContext):
    await state.set_state(ApplicationForm.insured_sum)
    await cb.message.edit_text(texts.ASK_SUM)
    await cb.answer()


# ─────────────────────── step 9-10 ───────────────────────
@router.message(ApplicationForm.insured_sum, F.text)
async def set_sum(message: Message, state: FSMContext):
    raw = message.text.replace(" ", "").replace(",", "")
    try:
        value = float(raw)
    except ValueError:
        await message.answer("Please enter a number, e.g. 5000000.")
        return
    await state.update_data(insured_sum=value)
    await state.set_state(ApplicationForm.term)
    await message.answer(
        texts.ASK_TERM, reply_markup=keyboards.options_kb(texts.TERMS, "term", columns=3)
    )


@router.callback_query(ApplicationForm.term, F.data.startswith("term:"))
async def set_term(cb: CallbackQuery, state: FSMContext):
    await state.update_data(term=cb.data.split(":", 1)[1])
    await state.set_state(ApplicationForm.q_alarm)
    await cb.message.edit_text(
        texts.ASK_ALARM, reply_markup=keyboards.options_kb(texts.YES_NO, "alarm", columns=2)
    )
    await cb.answer()


# ─────────────────────── step 11: additional yes/no questions ───────────────────────
# (callback prefix, label stored in extra, next state, next prompt, next prefix)
ADDITIONAL = [
    ("alarm", "Security alarm", ApplicationForm.q_cctv, texts.ASK_CCTV, "cctv"),
    ("cctv", "Video surveillance", ApplicationForm.q_claims, texts.ASK_CLAIMS, "claims"),
    ("claims", "Previous claims", ApplicationForm.q_tenants, texts.ASK_TENANTS, "tenants"),
    ("tenants", "Tenants present", ApplicationForm.q_vacant, texts.ASK_VACANT, "vacant"),
    ("vacant", "Currently vacant", ApplicationForm.q_business, texts.ASK_BUSINESS, "business"),
    ("business", "Used for business", None, None, None),
]
_ADD_BY_PREFIX = {p: (label, nxt, prompt, npfx) for p, label, nxt, prompt, npfx in ADDITIONAL}


@router.callback_query(F.data.regexp(r"^(alarm|cctv|claims|tenants|vacant|business):(yes|no)$"))
async def set_additional(cb: CallbackQuery, state: FSMContext):
    prefix, answer = cb.data.split(":", 1)
    label, nxt, prompt, npfx = _ADD_BY_PREFIX[prefix]
    data = await state.get_data()
    extra = dict(data.get("extra", {}))
    extra[label] = "Yes" if answer == "yes" else "No"
    await state.update_data(extra=extra)

    if nxt is None:
        # finished -> documents step
        await state.set_state(ApplicationForm.documents)
        await state.update_data(documents=[])
        await cb.message.edit_text(texts.ASK_DOCS)
        await cb.message.answer("⬆️ Send your files now.", reply_markup=keyboards.docs_done_kb())
    else:
        await state.set_state(nxt)
        await cb.message.edit_text(
            prompt, reply_markup=keyboards.options_kb(texts.YES_NO, npfx, columns=2)
        )
    await cb.answer()


# ─────────────────────── step 12: documents ───────────────────────
@router.message(ApplicationForm.documents, F.photo | F.document)
async def collect_document(message: Message, state: FSMContext):
    if message.photo:
        file_id = message.photo[-1].file_id
        ext = ".jpg"
    else:
        file_id = message.document.file_id
        ext = Path(message.document.file_name or "file").suffix or ".bin"

    # Download a local copy (best-effort; the Telegram file_id is always kept).
    file_path = None
    try:
        tg_file = await message.bot.get_file(file_id)
        dest = (
            settings.storage_dir
            / "documents"
            / f"{message.from_user.id}_{int(time.time() * 1000)}{ext}"
        )
        await message.bot.download_file(tg_file.file_path, destination=dest)
        file_path = str(dest)
    except Exception:
        pass

    data = await state.get_data()
    docs = list(data.get("documents", []))
    docs.append({"type": "document", "file_id": file_id, "file_path": file_path})
    await state.update_data(documents=docs)
    await message.answer(
        texts.DOC_SAVED.format(count=len(docs)), reply_markup=keyboards.docs_done_kb()
    )


@router.callback_query(ApplicationForm.documents, F.data == "docs_done")
async def documents_done(cb: CallbackQuery, state: FSMContext):
    await _show_review(cb.message, state)
    await cb.answer()


# ─────────────────────── step 13: review ───────────────────────
def _build_review(data: dict) -> str:
    addr = ", ".join(
        p
        for p in [
            data.get("postal_code"),
            data.get("country"),
            data.get("region"),
            data.get("city"),
            data.get("street"),
            data.get("house") and f"h.{data['house']}",
        ]
        if p
    )
    lines = [
        texts.REVIEW_TITLE,
        "",
        f"<b>Property type:</b> {texts.label_of(texts.PROPERTY_TYPES, data.get('property_type'))}",
        f"<b>Purpose:</b> {texts.label_of(texts.PURPOSES, data.get('purpose'))}",
        f"<b>Address:</b> {addr or '—'}",
        f"<b>Value:</b> {data.get('value', '—')}",
        f"<b>Owner:</b> {data.get('owner_name', '—')}",
        f"<b>Phone:</b> {data.get('phone', '—')}",
        f"<b>Coverage:</b> {texts.labels_of(texts.COVERAGE_OBJECTS, data.get('coverage'))}",
        f"<b>Risks:</b> {texts.labels_of(texts.RISKS, data.get('risks'))}",
        f"<b>Insured sum:</b> {data.get('insured_sum', '—')}",
        f"<b>Term:</b> {texts.label_of(texts.TERMS, data.get('term'))}",
        f"<b>Documents:</b> {len(data.get('documents', []))}",
    ]
    return "\n".join(lines)


async def _show_review(message: Message, state: FSMContext):
    await state.set_state(ApplicationForm.review)
    data = await state.get_data()
    await message.answer(_build_review(data), reply_markup=keyboards.review_kb())


@router.callback_query(ApplicationForm.review, F.data == "review_edit")
async def review_edit(cb: CallbackQuery, state: FSMContext):
    # MVP: restart the questionnaire. Granular per-field editing is a v2 item.
    await state.set_state(ApplicationForm.property_type)
    await cb.message.edit_text(
        texts.ASK_PROPERTY_TYPE, reply_markup=keyboards.options_kb(texts.PROPERTY_TYPES, "ptype")
    )
    await cb.answer("Starting over")


@router.callback_query(ApplicationForm.review, F.data == "review_submit")
async def review_submit(cb: CallbackQuery, state: FSMContext):
    await state.set_state(ApplicationForm.consent)
    await cb.message.edit_text(texts.CONSENT_TEXT, reply_markup=keyboards.consent_kb())
    await cb.answer()


# ─────────────────────── step 14: consent + submit ───────────────────────
@router.callback_query(ApplicationForm.consent, F.data == "consent_ok")
async def consent_ok(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    data["username"] = cb.from_user.username
    await cb.message.edit_text("✅ Consent recorded.")
    await cb.message.answer(texts.GEN_PDF)

    app = await repository.create_application(cb.from_user.id, data)

    pdf_path = generate_pdf(app)
    await cb.message.answer_document(
        FSInputFile(pdf_path), caption=f"Your application #{app.number}"
    )

    # External integrations (stubbed — see app/services/integrations.py)
    await integrations.send_email_notifications(app)
    await integrations.push_to_crm(app)
    await integrations.append_to_google_sheet(app)

    await state.clear()
    await cb.message.answer(
        texts.SUCCESS.format(number=app.number), reply_markup=keyboards.main_menu()
    )
    await cb.answer()
