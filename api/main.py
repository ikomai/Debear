"""REST API backend for the Debear mobile app.

Reuses the SAME database models, repository and validation as the Telegram
bot — so the bot and the app share one data store and identical business logic.

Run:  uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
Docs: http://localhost:8000/docs
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app import texts
from app.database import repository
from app.database.base import init_models
from app.services import validation
from app.services.pdf import generate_pdf

app = FastAPI(title="Debear API", version="1.0")

# Allow the Expo app (and any client) to call the API during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def _startup():
    await init_models()


# ─────────────────────── schemas ───────────────────────
def _opts(options):
    return [{"value": v, "label": l} for v, l in options]


class ValidateIn(BaseModel):
    value: str
    country: str | None = None
    city: str | None = None


class ApplicationIn(BaseModel):
    client_id: int  # device-generated id, used like a telegram_id
    property_type: str | None = None
    purpose: str | None = None
    # address
    country: str | None = None
    region: str | None = None
    city: str | None = None
    street: str | None = None
    house: str | None = None
    building: str | None = None
    apartment: str | None = None
    postal_code: str | None = None
    # property details
    year_built: str | None = None
    floors_total: str | None = None
    floor: str | None = None
    total_area: str | None = None
    living_area: str | None = None
    wall_material: str | None = None
    ceiling_material: str | None = None
    renovation: str | None = None
    value: str | None = None
    cadastral_number: str | None = None
    # owner
    owner_name: str | None = None
    birth_date: str | None = None
    gender: str | None = None
    phone: str | None = None
    email: str | None = None
    inn: str | None = None
    passport_series: str | None = None
    passport_number: str | None = None
    passport_issued_by: str | None = None
    passport_issue_date: str | None = None
    # mortgage
    has_mortgage: str | None = "no"
    bank: str | None = None
    contract_number: str | None = None
    contract_date: str | None = None
    debt_balance: str | None = None
    # policy
    coverage: list[str] = []
    risks: list[str] = []
    insured_sum: float | None = None
    term: str | None = None
    extra: dict = {}


# ─────────────────────── meta ───────────────────────
@app.get("/")
async def root():
    return {"ok": True, "service": "Debear API"}


@app.get("/api/meta")
async def meta():
    """Option lists — the app builds its UI from the same source as the bot."""
    return {
        "property_types": _opts(texts.PROPERTY_TYPES),
        "purposes": _opts(texts.PURPOSES),
        "renovation": _opts(texts.RENOVATION),
        "genders": _opts(texts.GENDERS),
        "coverage": _opts(texts.COVERAGE_OBJECTS),
        "risks": _opts(texts.RISKS),
        "terms": _opts(texts.TERMS),
        "status_labels": texts.STATUS_LABELS,
    }


# ─────────────────────── validation (same logic as the bot) ───────────────────────
@app.post("/api/validate/country")
async def validate_country(body: ValidateIn):
    r = await validation.validate_country(body.value, {})
    return {"ok": r.ok, "value": r.value, "message": r.message, "suggestions": r.suggestions}


@app.post("/api/validate/city")
async def validate_city(body: ValidateIn):
    r = await validation.validate_city(body.value, {"country": body.country})
    return {"ok": r.ok, "value": r.value, "message": r.message, "suggestions": r.suggestions}


@app.post("/api/validate/street")
async def validate_street(body: ValidateIn):
    r = await validation.validate_street(
        body.value, {"country": body.country, "city": body.city}
    )
    return {"ok": r.ok, "value": r.value, "message": r.message, "suggestions": r.suggestions}


# ─────────────────────── applications ───────────────────────
def _app_to_dict(a) -> dict:
    return {
        "id": a.id,
        "number": a.number,
        "status": a.status,
        "status_label": texts.STATUS_LABELS.get(a.status, a.status),
        "property_type": a.property_type,
        "property_type_label": texts.label_of(texts.PROPERTY_TYPES, a.property_type),
        "insured_sum": float(a.insured_sum) if a.insured_sum else None,
        "term_months": a.term_months,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }


@app.post("/api/applications")
async def create_application(body: ApplicationIn):
    data = body.model_dump()
    client_id = data.pop("client_id")
    data["documents"] = []  # file upload handled separately (see roadmap)
    application = await repository.create_application(client_id, data)
    generate_pdf(application)  # pre-generate the PDF
    return _app_to_dict(application)


@app.get("/api/applications")
async def list_applications(client_id: int):
    apps = await repository.list_user_applications(client_id)
    return [_app_to_dict(a) for a in apps]


@app.get("/api/applications/{app_id}")
async def get_application(app_id: int):
    a = await repository.get_application(app_id)
    if a is None:
        raise HTTPException(404, "Application not found")
    result = _app_to_dict(a)
    result["coverage"] = texts.labels_of(texts.COVERAGE_OBJECTS, a.coverage)
    result["risks"] = texts.labels_of(texts.RISKS, a.risks)
    result["address"] = a.property.full_address if a.property else None
    result["owner"] = a.owner.full_name if a.owner else None
    return result


@app.get("/api/applications/{app_id}/pdf")
async def application_pdf(app_id: int):
    a = await repository.get_application(app_id)
    if a is None:
        raise HTTPException(404, "Application not found")
    path = generate_pdf(a)
    return FileResponse(path, media_type="application/pdf", filename=path.name)
