"""Finite-state-machine states for the application questionnaire."""
from aiogram.fsm.state import State, StatesGroup


class ApplicationForm(StatesGroup):
    # Step 1-2
    property_type = State()
    purpose = State()
    # Step 3 — address
    country = State()
    region = State()
    city = State()
    street = State()
    house = State()
    building = State()
    apartment = State()
    postal_code = State()
    # Step 4 — property details
    year_built = State()
    floors_total = State()
    floor = State()
    total_area = State()
    living_area = State()
    wall_material = State()
    ceiling_material = State()
    renovation = State()
    value = State()
    cadastral_number = State()
    # Step 5 — owner
    owner_name = State()
    birth_date = State()
    gender = State()
    phone = State()
    email = State()
    inn = State()
    passport_series = State()
    passport_number = State()
    passport_issued_by = State()
    passport_issue_date = State()
    # Step 6 — mortgage
    has_mortgage = State()
    bank = State()
    contract_number = State()
    contract_date = State()
    debt_balance = State()
    # Step 7-10
    coverage = State()
    risks = State()
    insured_sum = State()
    term = State()
    # Step 11 — additional questions
    q_alarm = State()
    q_cctv = State()
    q_claims = State()
    q_tenants = State()
    q_vacant = State()
    q_business = State()
    # Step 12-13
    documents = State()
    review = State()
    consent = State()
