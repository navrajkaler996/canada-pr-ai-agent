"""
Test script for User B — Currently on study permit doing a Master's in Canada.
Tests current score vs projected score after graduation + 1 year NOC A work.

Run from backend directory:
    python test_user_b_masters.py
"""

from crs_calculator import calculate_crs
from datetime import datetime

# ─── USER B PROFILE ───────────────────────────────────────────────────────────
# Born: 1996
# Current age: 2026 - 1996 = 30
# Doing: Master's degree in Canada
# Expected graduation: 2028
# Eligibility year: 2029
# Projected age at eligibility: 2029 - 1996 = 33

BIRTH_YEAR = 1996
GRADUATION_YEAR = 2028
CURRENT_YEAR = datetime.now().year
ELIGIBILITY_YEAR = GRADUATION_YEAR + 1

CURRENT_AGE = CURRENT_YEAR - BIRTH_YEAR
PROJECTED_AGE = ELIGIBILITY_YEAR - BIRTH_YEAR

print(f"Birth year: {BIRTH_YEAR}")
print(f"Current age: {CURRENT_AGE}")
print(f"Graduation year: {GRADUATION_YEAR}")
print(f"Eligibility year: {ELIGIBILITY_YEAR}")
print(f"Projected age at eligibility: {PROJECTED_AGE}")
print()

# ─── CURRENT PROFILE (today, no Canadian work experience) ─────────────────────

current_profile = {
    "has_spouse": False,
    "age": CURRENT_AGE,
    "education": "bachelors",           # completed before coming to Canada
    "clb_speaking": 9,
    "clb_listening": 11,
    "clb_reading": 11,
    "clb_writing": 11,
    "canadian_work_years": 0,
    "foreign_work_years": 3,
    "first_language": "english",
    "has_canadian_sibling": False,
    "french_clb_scores": [],
    "canadian_education_years": 0,      # masters not yet complete
    "has_provincial_nomination": False,
    "has_certificate": False,
    "job_offer": False,
    "trade_certificate": False,
    "second_language_test": "none",
    "canadian_noc": None,
    "foreign_noc": "A",
    "spouse_education": None,
    "spouse_clb_speaking": None,
    "spouse_clb_listening": None,
    "spouse_clb_reading": None,
    "spouse_clb_writing": None,
    "spouse_canadian_work_years": None,
}

# ─── PROJECTED PROFILE (after graduation + 1 year NOC A work) ─────────────────

projected_profile = {
    **current_profile,
    "age": PROJECTED_AGE,               # age at eligibility
    "education": "masters",             # masters completed
    "canadian_work_years": 1,           # 1 year NOC A work
    "canadian_noc": "A",
    "canadian_education_years": 3,      # masters = 3+ years for CRS purposes
}

# ─── CALCULATE ────────────────────────────────────────────────────────────────

current_result = calculate_crs(current_profile)
projected_result = calculate_crs(projected_profile)

# ─── PRINT RESULTS ────────────────────────────────────────────────────────────

print("=" * 50)
print("CURRENT SCORE (today)")
print("=" * 50)
print(f"Total CRS: {current_result['total']}")
print()
for key, val in current_result["breakdown"].items():
    print(f"  {key:<20} {val}")

print()
print("=" * 50)
print(f"PROJECTED SCORE (after graduation {GRADUATION_YEAR} + 1 year work)")
print("=" * 50)
print(f"Total CRS: {projected_result['total']}")
print()
for key, val in projected_result["breakdown"].items():
    print(f"  {key:<20} {val}")

print()
print("=" * 50)
print("DELTA (what changes)")
print("=" * 50)
print(f"Score gain: +{projected_result['total'] - current_result['total']} points")
print()
for key in current_result["breakdown"]:
    current_val = current_result["breakdown"][key]
    projected_val = projected_result["breakdown"][key]
    delta = projected_val - current_val
    if delta != 0:
        print(f"  {key:<20} {current_val} → {projected_val} ({'+' if delta > 0 else ''}{delta})")