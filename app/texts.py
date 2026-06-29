"""All user-facing strings (English). Centralised for easy localisation later."""

# ─────────── Main menu ───────────
MENU_NEW = "🏠 Apply for insurance"
MENU_MY_APPS = "📋 My applications"
MENU_DOCS = "📄 Documents"
MENU_HELP = "❓ Help"
MENU_CONTACT = "☎ Contact a manager"

WELCOME = (
    "Hello!\n\n"
    "This bot helps you apply for real-estate insurance.\n"
    "It takes about 5 minutes to complete."
)

HELP = (
    "<b>How it works</b>\n\n"
    "1. Tap <i>Apply for insurance</i> and answer the questions step by step.\n"
    "2. Attach the requested documents.\n"
    "3. Review your application and submit it.\n"
    "4. A manager will contact you, and you can track the status in "
    "<i>My applications</i>.\n\n"
    "Use /start at any time to return to the main menu, or /cancel to stop "
    "the current application."
)

CONTACT = (
    "☎ <b>Contact a manager</b>\n\n"
    "Write to @Ur_Oper or call +0 000 000-00-00.\n"
    "Working hours: Mon–Fri, 9:00–18:00."
)

# ─────────── Flow ───────────
BTN_BEGIN = "Begin application"
ASK_PROPERTY_TYPE = "Step 1 / 13 — What type of property do you want to insure?"
ASK_PURPOSE = "Step 2 / 13 — What is the purpose of the insurance?"

ASK_COUNTRY = "Step 3 / 13 — Property address.\n\nEnter the <b>country</b>:"
ASK_REGION = "Enter the <b>region / state</b>:"
ASK_CITY = "Enter the <b>city</b>:"
ASK_STREET = "Enter the <b>street</b>:"
ASK_HOUSE = "Enter the <b>house number</b>:"
ASK_BUILDING = "Enter the <b>building / block</b> (or “-” if none):"
ASK_APARTMENT = "Enter the <b>apartment number</b> (or “-” if none):"
ASK_POSTAL = "Enter the <b>postal code</b>:"

ASK_YEAR_BUILT = "Step 4 / 13 — Property details.\n\nYear of construction:"
ASK_FLOORS_TOTAL = "Total number of floors in the building:"
ASK_FLOOR = "Floor the property is on:"
ASK_TOTAL_AREA = "Total area, m²:"
ASK_LIVING_AREA = "Living area, m²:"
ASK_WALL_MATERIAL = "Wall material (e.g. brick, concrete, wood):"
ASK_CEILING_MATERIAL = "Ceiling / floor material (e.g. reinforced concrete, wood):"
ASK_RENOVATION = "Renovation condition:"
ASK_VALUE = "Estimated property value (in your currency):"
ASK_CADASTRAL = "Cadastral number (optional — send “-” to skip):"

ASK_OWNER_NAME = "Step 5 / 13 — Owner details.\n\nFull name:"
ASK_BIRTH_DATE = "Date of birth (DD.MM.YYYY):"
ASK_GENDER = "Gender:"
ASK_PHONE = "Phone number:"
ASK_EMAIL = "Email:"
ASK_INN = "Tax ID / INN (optional — send “-” to skip):"
ASK_PASSPORT_SERIES = "Passport series:"
ASK_PASSPORT_NUMBER = "Passport number:"
ASK_PASSPORT_ISSUED = "Passport issued by:"
ASK_PASSPORT_DATE = "Passport issue date (DD.MM.YYYY):"

ASK_MORTGAGE = "Step 6 / 13 — Is the property under a mortgage?"
ASK_BANK = "Bank name:"
ASK_CONTRACT_NUMBER = "Mortgage contract number:"
ASK_CONTRACT_DATE = "Mortgage contract date (DD.MM.YYYY):"
ASK_DEBT = "Outstanding debt balance:"

ASK_COVERAGE = "Step 7 / 13 — What do you want to insure? (select all that apply)"
ASK_RISKS = "Step 8 / 13 — Which risks should be covered? (select all that apply)"
ASK_SUM = "Step 9 / 13 — Enter the desired insured sum (number):"
ASK_TERM = "Step 10 / 13 — Insurance term:"

ASK_ALARM = "Step 11 / 13 — Additional questions.\n\nIs there a security alarm?"
ASK_CCTV = "Is there video surveillance (CCTV)?"
ASK_CLAIMS = "Have there been any insurance claims before?"
ASK_TENANTS = "Are there any tenants?"
ASK_VACANT = "Is the property currently vacant?"
ASK_BUSINESS = "Is the property used for business?"

ASK_DOCS = (
    "Step 12 / 13 — Attach documents.\n\n"
    "Send photos or files one by one (passport, title, EGRN extract, mortgage "
    "contract, photos of the property, etc.).\n"
    "Supported: PDF, JPEG, PNG, HEIC.\n\n"
    "When you are done, tap <b>Done</b>."
)
DOC_SAVED = "✅ Document saved ({count} total). Send another or tap <b>Done</b>."
BTN_DOCS_DONE = "Done"

REVIEW_TITLE = "Step 13 / 13 — Please review your application:"
BTN_EDIT = "✏️ Edit (start over)"
BTN_SUBMIT = "✅ Submit"

CONSENT_TEXT = (
    "Before submitting, please confirm:\n\n"
    "“I agree to the processing of my personal data.”\n\n"
    "Submission is not possible without consent."
)
BTN_CONSENT = "✅ I agree"

SUCCESS = (
    "Thank you!\n\n"
    "Your application <b>#{number}</b> has been submitted.\n"
    "A manager will contact you shortly.\n\n"
    "You can track its status in 📋 <i>My applications</i>."
)

CANCELLED = "Application cancelled. Use /start to open the main menu."
NO_APPS = "You don't have any applications yet."
GEN_PDF = "📄 Generating your application PDF…"

# ─────────── Option lists (value -> label) ───────────
PROPERTY_TYPES = [
    ("apartment", "🏢 Apartment"),
    ("house", "🏠 House"),
    ("townhouse", "🏡 Townhouse"),
    ("aparts", "🏘 Apartments"),
    ("commercial", "🏭 Commercial property"),
]

PURPOSES = [
    ("mortgage", "Mortgage"),
    ("voluntary", "Voluntary insurance"),
    ("renewal", "Renewal"),
    ("new", "New policy"),
]

RENOVATION = [
    ("none", "No renovation"),
    ("cosmetic", "Cosmetic"),
    ("standard", "Standard"),
    ("euro", "Premium / euro"),
    ("designer", "Designer"),
]

GENDERS = [("male", "Male"), ("female", "Female")]

COVERAGE_OBJECTS = [
    ("structure", "Structure"),
    ("interior", "Interior finishing"),
    ("engineering", "Engineering equipment"),
    ("furniture", "Furniture"),
    ("appliances", "Home appliances"),
    ("liability", "Civil liability"),
    ("outbuildings", "Outbuildings"),
]

RISKS = [
    ("fire", "Fire"),
    ("flood", "Flooding"),
    ("disaster", "Natural disasters"),
    ("explosion", "Explosion"),
    ("theft", "Theft"),
    ("illegal", "Unlawful acts"),
    ("trees", "Falling trees"),
    ("aircraft", "Falling aircraft"),
    ("water", "Water damage"),
    ("all", "All risks"),
]

TERMS = [
    ("6", "6 months"),
    ("12", "12 months"),
    ("24", "24 months"),
]

YES_NO = [("yes", "Yes"), ("no", "No")]


def label_of(options, value, default="—"):
    """Return the human label for a stored option value."""
    for val, lbl in options:
        if val == value:
            return lbl
    return default or value


def labels_of(options, values):
    """Return a comma-separated list of labels for a list of values."""
    if not values:
        return "—"
    return ", ".join(label_of(options, v) for v in values)


# ─────────── Application statuses ───────────
STATUSES = [
    "draft",
    "filling",
    "submitted",
    "in_review",
    "awaiting_docs",
    "approved",
    "rejected",
    "policy_issued",
    "closed",
]

STATUS_LABELS = {
    "draft": "Draft",
    "filling": "Being filled",
    "submitted": "Submitted",
    "in_review": "In review",
    "awaiting_docs": "Awaiting documents",
    "approved": "Approved",
    "rejected": "Rejected",
    "policy_issued": "Policy issued",
    "closed": "Closed",
}
