# Real-Estate Insurance Bot (Telegram)

A Telegram bot that walks a client through a step-by-step real-estate
insurance application, stores it in a database, generates a PDF, and lets an
admin manage statuses.

Built with **Python + aiogram 3**. Interface language: **English**.

This repo now contains three parts that all share the same database & logic:
- **`app/`** — the Telegram bot (aiogram).
- **`api/`** — a FastAPI REST backend (reuses the bot's models, repository and
  validation).
- **`mobile/`** — the **Debear** mobile app (Expo / React Native) that talks to
  the backend. See [mobile/README.md](mobile/README.md).

---

## Features (MVP)

- 🏠 Main menu (`/start`)
- 📝 Full step-by-step questionnaire (property → address → details → owner →
  mortgage → coverage → risks → sum → term → extra questions → documents →
  review → consent → submit)
- 🗄 Stores data in **SQLite** (default, zero setup) or **MySQL** (production)
- 📄 Automatic **PDF** generation with a QR code
- 📎 Document upload (PDF / JPEG / PNG / HEIC)
- 📋 “My applications” with statuses
- 🛠 Basic admin panel (`/admin`) to view applications and change status, with
  automatic client notification

### Intentionally out of MVP scope (from the larger spec)
CRM API push, transactional email, Google Sheets / 1C export, S3 file storage,
Redis queues, Excel/CSV export, granular per-field editing, online price
calculation, payments, WebApp forms, OCR. Integration points are stubbed in
`app/services/integrations.py` so they are easy to fill in per client.

---

## Quick start (Windows / PowerShell)

```powershell
cd "$env:USERPROFILE\Desktop\UpWork_TG"

# 1. (optional but recommended) create a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. install dependencies
pip install -r requirements.txt

# 3. configure the bot
#    - open .env
#    - paste the token from @BotFather into BOT_TOKEN
#    - put your Telegram numeric id (from @userinfobot) into ADMIN_IDS

# 4. run
python run.py
```

Then open your bot in Telegram and send `/start`.

---

## Input validation ("real data")

The questionnaire checks answers before accepting them (`app/services/validation.py`):

| Field | Check | On error |
|-------|-------|----------|
| Country | Real country (ISO list + common aliases) | Offers "did you mean" buttons; must pick a valid one |
| City | Exists in the chosen country (OSM Nominatim) | Suggests the correct spelling, or keep-as-typed |
| Street | Exists in the chosen city (OSM Nominatim) | Suggests the correct spelling, or keep-as-typed |
| Email / Phone | Format check | Asks to re-enter |
| Dates (birth, passport) | Valid `DD.MM.YYYY`, realistic year | Asks to re-enter |
| Year built / areas / value | Numeric, sensible range | Asks to re-enter |

> ⚠️ **Geocoder note:** city/street use the **free OpenStreetMap Nominatim**
> API (no key). Its free tier allows ~1 request/second and returns **HTTP 403**
> under bursts/load. When the geocoder is unreachable the value is
> *soft-accepted* so users are never blocked — meaning under heavy load address
> checks effectively pass through. **For production, swap to a paid geocoder**
> (Google Places, LocationIQ, Dadata) — only the `_search()` function needs to
> change. Country and all format checks are fully offline and unaffected.

## Database

The data layer (SQLAlchemy async) works with both engines — only `.env` changes.

| `DB_ENGINE` | Use case | Notes |
|-------------|----------|-------|
| `sqlite` (default) | local development | creates `bot.db`, no setup |
| `mysql` | production | uses the `MYSQL_*` values in `.env` |

Tables are created automatically on first run. A ready-to-run
`schema.sql` is also included for MySQL Workbench.

> ⚠️ **Remote MySQL note:** the provided host `cfif31.ru:3306` refused direct
> connections from outside (typical for shared hosting — MySQL is reachable
> only from the hosting server). To use MySQL you need either remote access
> enabled for your IP, or to run the bot on the hosting itself. Until then the
> bot runs perfectly on the default SQLite engine.

> 🔒 **Security:** never commit `.env`. The DB password was shared in plain
> text — rotate it in your hosting panel.

---

## Project structure

```
UpWork_TG/
├─ run.py                    # entry point (long polling)
├─ requirements.txt
├─ schema.sql                # MySQL DDL for Workbench
├─ .env / .env.example       # configuration
└─ app/
   ├─ config.py              # settings from .env
   ├─ texts.py               # all UI strings + option lists (English)
   ├─ states.py              # FSM states
   ├─ keyboards.py           # keyboard builders
   ├─ database/
   │  ├─ base.py             # async engine / session
   │  ├─ models.py           # ORM models (users, applications, property, …)
   │  └─ repository.py       # CRUD helpers
   ├─ services/
   │  ├─ pdf.py              # ReportLab PDF + QR code
   │  └─ integrations.py     # CRM / email / sheets stubs
   └─ handlers/
      ├─ common.py           # /start, menu, help, cancel
      ├─ application.py      # the questionnaire (FSM)
      ├─ my_apps.py          # personal cabinet
      └─ admin.py            # admin panel
```

---

## Commands

| Command | Who | What |
|---------|-----|------|
| `/start` | everyone | open the main menu |
| `/cancel` | everyone | abort the current application |
| `/admin` | admins only | list applications, change status |
