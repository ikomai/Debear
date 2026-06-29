"""Generate a PDF summary of an application, including a QR code."""
from __future__ import annotations

import io
from datetime import datetime
from pathlib import Path

import qrcode
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app import texts
from app.config import settings
from app.database.models import Application


def _qr_image(payload: str) -> io.BytesIO:
    img = qrcode.make(payload)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def _section(title: str, rows: list[tuple[str, str]], styles) -> list:
    elements = [Paragraph(title, styles["Heading3"])]
    data = [[Paragraph(f"<b>{k}</b>", styles["Cell"]), Paragraph(v or "—", styles["Cell"])] for k, v in rows]
    table = Table(data, colWidths=[55 * mm, 110 * mm])
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#DDDDDD")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elements.append(table)
    elements.append(Spacer(1, 6 * mm))
    return elements


def generate_pdf(app: Application) -> Path:
    """Render the application into a PDF file and return its path."""
    out_path = settings.storage_dir / "pdf" / f"application_{app.number}.pdf"
    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=f"Insurance application #{app.number}",
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Cell", fontSize=9, leading=12))
    title_style = ParagraphStyle(
        name="DocTitle", parent=styles["Title"], fontSize=18, spaceAfter=2
    )

    story: list = []
    story.append(Paragraph("Real-Estate Insurance Application", title_style))
    story.append(
        Paragraph(
            f"No. {app.number} &nbsp;·&nbsp; {datetime.now():%d.%m.%Y %H:%M}",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 8 * mm))

    prop = app.property
    owner = app.owner

    story += _section(
        "Policy",
        [
            ("Property type", texts.label_of(texts.PROPERTY_TYPES, app.property_type)),
            ("Purpose", texts.label_of(texts.PURPOSES, app.purpose)),
            ("Insured sum", f"{app.insured_sum:,.2f}" if app.insured_sum else "—"),
            ("Term", f"{app.term_months} months" if app.term_months else "—"),
            ("Coverage", texts.labels_of(texts.COVERAGE_OBJECTS, app.coverage)),
            ("Risks", texts.labels_of(texts.RISKS, app.risks)),
        ],
        styles,
    )

    if prop:
        story += _section(
            "Property",
            [
                ("Address", prop.full_address),
                ("Year built", prop.year_built),
                ("Floors / floor", f"{prop.floors_total} / {prop.floor}"),
                ("Total / living area", f"{prop.total_area} / {prop.living_area} m²"),
                ("Wall material", prop.wall_material),
                ("Ceiling material", prop.ceiling_material),
                ("Renovation", texts.label_of(texts.RENOVATION, prop.renovation)),
                ("Declared value", prop.value),
                ("Cadastral no.", prop.cadastral_number),
            ],
            styles,
        )

    if owner:
        story += _section(
            "Owner",
            [
                ("Full name", owner.full_name),
                ("Date of birth", owner.birth_date),
                ("Gender", texts.label_of(texts.GENDERS, owner.gender)),
                ("Phone", owner.phone),
                ("Email", owner.email),
                ("Tax ID / INN", owner.inn),
                (
                    "Passport",
                    f"{owner.passport_series or ''} {owner.passport_number or ''}, "
                    f"issued {owner.passport_issue_date or ''} by {owner.passport_issued_by or ''}",
                ),
            ],
            styles,
        )

    if app.has_mortgage:
        story += _section(
            "Mortgage",
            [
                ("Bank", app.bank),
                ("Contract no.", app.contract_number),
                ("Contract date", app.contract_date),
                ("Debt balance", app.debt_balance),
            ],
            styles,
        )

    extra = app.extra or {}
    if extra:
        story += _section("Additional", [(k, str(v)) for k, v in extra.items()], styles)

    story += _section(
        "Documents",
        [("Attached files", str(len(app.documents)))],
        styles,
    )

    # QR code with the application reference
    qr_payload = f"INSURANCE-APP;NUMBER={app.number};SUM={app.insured_sum}"
    story.append(Image(_qr_image(qr_payload), width=30 * mm, height=30 * mm))
    story.append(Paragraph("Scan to reference this application", styles["Cell"]))
    story.append(Spacer(1, 4 * mm))
    story.append(
        Paragraph("Client signature: ____________________", styles["Normal"])
    )

    doc.build(story)
    return out_path
