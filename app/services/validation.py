"""Input validation: real-world checks (country / city / street) and formats.

- Country is validated against the ISO country list (pycountry) with fuzzy
  "did you mean" suggestions.
- City and street are validated through the OpenStreetMap Nominatim geocoder.
  If the geocoder is unreachable, the value is soft-accepted so the user is
  never blocked by a temporary outage.
- Email / phone / dates / numbers are validated by format.

NOTE: Nominatim's free usage policy allows ~1 request/second and requires a
valid User-Agent. For production volume, switch to a paid geocoder (Google
Places, Dadata, etc.) — only `_search` below needs to change.
"""
from __future__ import annotations

import difflib
import re
from dataclasses import dataclass, field
from datetime import datetime

import aiohttp
import pycountry

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "RealEstateInsuranceBot/1.0 (support@example.com)"
TIMEOUT = aiohttp.ClientTimeout(total=8)


@dataclass
class ValidationResult:
    ok: bool
    value: str | None = None              # cleaned / canonical value to store
    message: str | None = None            # prompt shown when ok is False
    suggestions: list[str] = field(default_factory=list)


# Common short names / colloquial spellings that pycountry doesn't index.
_COMMON_ALIASES = {
    "Russia": "Russian Federation",
    "USA": "United States", "US": "United States", "America": "United States",
    "UK": "United Kingdom", "England": "United Kingdom",
    "Britain": "United Kingdom", "Great Britain": "United Kingdom",
    "South Korea": "Korea, Republic of",
    "North Korea": "Korea, Democratic People's Republic of",
    "Iran": "Iran, Islamic Republic of", "Syria": "Syrian Arab Republic",
    "Vietnam": "Viet Nam", "Venezuela": "Venezuela, Bolivarian Republic of",
    "Bolivia": "Bolivia, Plurinational State of",
    "Tanzania": "Tanzania, United Republic of", "Moldova": "Moldova, Republic of",
    "Czech Republic": "Czechia", "Turkey": "Türkiye",
    "Laos": "Lao People's Democratic Republic", "Brunei": "Brunei Darussalam",
}


# Index of every recognised country name/alias -> canonical ISO name.
def _build_country_index() -> dict[str, str]:
    index: dict[str, str] = {}
    for c in pycountry.countries:
        for attr in ("name", "official_name", "common_name"):
            alias = getattr(c, attr, None)
            if alias:
                index[alias] = c.name
    index.update(_COMMON_ALIASES)
    return index


_COUNTRY_INDEX = _build_country_index()
_COUNTRY_KEYS = list(_COUNTRY_INDEX)
_COUNTRY_INDEX_LOWER = {k.lower(): v for k, v in _COUNTRY_INDEX.items()}


def _similar(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


# ─────────────────────── country ───────────────────────
async def validate_country(value: str, data: dict) -> ValidationResult:
    value = value.strip()
    if not value:
        return ValidationResult(False, message="Please enter a country name.")
    try:
        return ValidationResult(True, value=pycountry.countries.lookup(value).name)
    except LookupError:
        pass
    if value.lower() in _COUNTRY_INDEX_LOWER:  # common alias, e.g. "Russia", "UK"
        return ValidationResult(True, value=_COUNTRY_INDEX_LOWER[value.lower()])

    # Fuzzy "did you mean": try pycountry, then fall back to difflib on all aliases.
    suggestions: list[str] = []
    try:
        suggestions = [c.name for c in pycountry.countries.search_fuzzy(value)]
    except LookupError:
        suggestions = []
    if not suggestions:
        close = difflib.get_close_matches(value.title(), _COUNTRY_KEYS, n=3, cutoff=0.6)
        suggestions = list(dict.fromkeys(_COUNTRY_INDEX[k] for k in close))
    suggestions = suggestions[:3]

    return ValidationResult(
        False,
        message=f"I couldn't recognize the country “{value}”."
        + (" Did you mean:" if suggestions else " Please check the spelling and try again."),
        suggestions=suggestions,
    )


# ─────────────────────── geocoding (city / street) ───────────────────────
async def _search(params: dict) -> list[dict]:
    params = {**params, "format": "json", "addressdetails": 1, "limit": 5, "accept-language": "en"}
    async with aiohttp.ClientSession(headers={"User-Agent": USER_AGENT}) as session:
        async with session.get(NOMINATIM_URL, params=params, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                raise RuntimeError(f"geocoder status {resp.status}")
            return await resp.json()


def _pick(addr: dict, *keys: str) -> str | None:
    for key in keys:
        if addr.get(key):
            return addr[key]
    return None


async def validate_city(value: str, data: dict) -> ValidationResult:
    value = value.strip()
    country = data.get("country") or ""
    try:
        results = await _search({"country": country, "city": value})
    except Exception:
        return ValidationResult(True, value=value.title())  # soft-accept on outage

    if results:
        canonical = _pick(
            results[0].get("address", {}), "city", "town", "village", "municipality", "county"
        ) or results[0].get("display_name", "").split(",")[0].strip()
        if not canonical:
            return ValidationResult(True, value=value.title())
        # Nominatim is lenient: if it corrected a typo, ask the user to confirm.
        if _similar(canonical, value) >= 0.93:
            return ValidationResult(True, value=canonical)
        return ValidationResult(
            False, message="Did you mean this city:", suggestions=[canonical]
        )

    # not found -> gather close alternatives
    try:
        alt = await _search({"q": f"{value}, {country}"})
    except Exception:
        alt = []
    seen, suggestions = set(), []
    for item in alt:
        name = _pick(item.get("address", {}), "city", "town", "village", "municipality", "state")
        if name and name.lower() not in seen:
            seen.add(name.lower())
            suggestions.append(name)
    return ValidationResult(
        False,
        message=f"I couldn't find the city “{value}” in {country}."
        + (" Did you mean:" if suggestions else " You can keep it as typed."),
        suggestions=suggestions[:4],
    )


async def validate_street(value: str, data: dict) -> ValidationResult:
    value = value.strip()
    country = data.get("country") or ""
    city = data.get("city") or ""
    try:
        results = await _search({"country": country, "city": city, "street": value})
    except Exception:
        return ValidationResult(True, value=value.title())  # soft-accept on outage

    if results:
        road = _pick(results[0].get("address", {}), "road", "pedestrian", "footway")
        if not road:
            return ValidationResult(True, value=value.title())
        if _similar(road, value) >= 0.93:
            return ValidationResult(True, value=road)
        return ValidationResult(
            False, message="Did you mean this street:", suggestions=[road]
        )

    try:
        alt = await _search({"q": f"{value}, {city}, {country}"})
    except Exception:
        alt = []
    seen, suggestions = set(), []
    for item in alt:
        road = _pick(item.get("address", {}), "road", "pedestrian", "footway")
        if road and road.lower() not in seen:
            seen.add(road.lower())
            suggestions.append(road)
    return ValidationResult(
        False,
        message=f"I couldn't find the street “{value}” in {city}."
        + (" Did you mean:" if suggestions else " You can keep it as typed."),
        suggestions=suggestions[:4],
    )


# ─────────────────────── format validators ───────────────────────
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


async def validate_email(value: str, data: dict) -> ValidationResult:
    value = value.strip()
    if _EMAIL_RE.match(value):
        return ValidationResult(True, value=value)
    return ValidationResult(False, message="That doesn't look like a valid email. Example: name@example.com")


async def validate_phone(value: str, data: dict) -> ValidationResult:
    digits = re.sub(r"\D", "", value)
    if 7 <= len(digits) <= 15:
        return ValidationResult(True, value=value.strip())
    return ValidationResult(
        False, message="Please enter a valid phone number (7–15 digits), e.g. +1 555 0100."
    )


async def validate_date(value: str, data: dict) -> ValidationResult:
    value = value.strip()
    try:
        dt = datetime.strptime(value, "%d.%m.%Y")
    except ValueError:
        return ValidationResult(False, message="Please use the format DD.MM.YYYY, e.g. 31.12.1990.")
    if not (1900 <= dt.year <= datetime.now().year):
        return ValidationResult(False, message="Please enter a realistic date (year 1900–today).")
    return ValidationResult(True, value=value)


async def validate_year(value: str, data: dict) -> ValidationResult:
    value = value.strip()
    if not value.isdigit() or not (1800 <= int(value) <= datetime.now().year):
        return ValidationResult(
            False, message=f"Please enter a valid construction year (1800–{datetime.now().year})."
        )
    return ValidationResult(True, value=value)


async def validate_positive_number(value: str, data: dict) -> ValidationResult:
    cleaned = value.replace(" ", "").replace(",", "")
    try:
        number = float(cleaned)
    except ValueError:
        return ValidationResult(False, message="Please enter a number (digits only), e.g. 72.5")
    if number <= 0:
        return ValidationResult(False, message="The value must be greater than zero.")
    return ValidationResult(True, value=str(number if number % 1 else int(number)))
