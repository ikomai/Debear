"""Stubs for external integrations described in the spec.

These are intentionally light: they log what *would* be sent so the flow is
complete and the integration points are obvious. Fill them in per client.
"""
from __future__ import annotations

import logging

from app.database.models import Application

log = logging.getLogger(__name__)


async def push_to_crm(app: Application) -> None:
    """Send the application to an external CRM via its API.

    TODO: replace with a real httpx POST to the client's CRM endpoint,
    mapping client / object / documents / status fields.
    """
    log.info("[CRM] would push application #%s (status=%s)", app.number, app.status)


async def send_email_notifications(app: Application) -> None:
    """Email the client and the manager after submission.

    TODO: integrate SMTP / a transactional email provider (SendGrid, etc.).
    """
    log.info("[EMAIL] would notify client (%s) and manager about #%s", app.owner.email, app.number)


async def append_to_google_sheet(app: Application) -> None:
    """Append the application as a row in a Google Sheet (optional).

    TODO: integrate gspread / Google Sheets API with a service account.
    """
    log.info("[SHEETS] would append a row for application #%s", app.number)
