# fsw_calculator.py
# Calculates the Federal Skilled Worker (FSW) 67-point selection grid.
# Also checks minimum eligibility requirements before running the grid.

def get_fsw_language_points(clb_scores):
    """
    Max 28 points.
    First language: up to 24 points (4 abilities x 6 max each)
    Second language: up to 4 points (4 abilities x 1 max each)
    """
    def clb_to_first_lang_points(clb):
        if clb >= 9: return 6
        if clb == 8: return 5
        if clb == 7: return 4
        if clb == 6: return 2
        if clb == 5: return 1
        return 0  # CLB 4 or below = 0

    first_lang = sum(clb_to_first_lang_points(c) for c in clb_scores[:4])
    first_lang = min(24, first_lang)

    # Second language (if provided, indices 4-7)
    second_lang = 0
    if len(clb_scores) > 4:
        def clb_to_second_lang_points(clb):
            if clb >= 5: return 1
            return 0
        second_lang = sum(clb_to_second_lang_points(c) for c in clb_scores[4:8])
        second_lang = min(4, second_lang)

    return min(28, first_lang + second_lang)


def get_fsw_education_points(education_level):
    """Max 25 points."""
    points = {
        "less_than_high_school": 0,
        "high_school":           5,
        "one_year":              15,
        "two_year":              19,
        "bachelors":             21,
        "two_or_more":           22,
        "masters":               23,
        "phd":                   25,
    }
    return points.get(education_level, 0)


def get_fsw_experience_points(total_years):
    """
    Max 15 points.
    Based on total skilled work experience (Canadian + foreign combined).
    """
    if total_years >= 6: return 15
    if total_years >= 4: return 13
    if total_years >= 2: return 11
    if total_years >= 1: return 9
    return 0


def get_fsw_age_points(age):
    """Max 12 points."""
    if 18 <= age <= 35: return 12
    if age == 36: return 10
    if age == 37: return 8
    if age == 38: return 6
    if age == 39: return 4
    if age == 40: return 2
    if age == 41: return 1
    return 0  # 42+


def get_fsw_arranged_employment_points(has_job_offer):
    """Max 10 points."""
    return 10 if has_job_offer else 0


def get_fsw_adaptability_points(profile):
    """
    Max 10 points.
    Spouse language CLB 4+    = 5 pts
    Previous Canadian study   = 5 pts
    Previous Canadian work    = 5 pts
    Relative in Canada        = 5 pts
    Arranged employment       = 5 pts (same as job offer)
    """
    total = 0

    # Spouse language (CLB 4+ in at least one ability)
    if profile.get("has_spouse"):
        spouse_clbs = [
            profile.get("spouse_clb_speaking", 0),
            profile.get("spouse_clb_listening", 0),
            profile.get("spouse_clb_reading", 0),
            profile.get("spouse_clb_writing", 0),
        ]
        if any(c >= 4 for c in spouse_clbs):
            total += 5

    # Canadian education (1+ years)
    if profile.get("canadian_education_years", 0) >= 1:
        total += 5

    # Canadian work experience (1+ years)
    if profile.get("canadian_work_years", 0) >= 1:
        total += 5

    # Relative in Canada (sibling counts)
    if profile.get("has_canadian_sibling", False):
        total += 5

    # Arranged employment
    if profile.get("job_offer", False):
        total += 5

    return min(10, total)


def check_fsw_minimum_requirements(profile):
    """
    Before running the grid, check if the user meets FSW minimum requirements.
    Returns (eligible: bool, reason: str)
    """
    foreign_years = profile.get("foreign_work_years", 0)
    foreign_noc   = profile.get("foreign_noc", None)
    canadian_years = profile.get("canadian_work_years", 0)
    canadian_noc  = profile.get("canadian_noc", None)
    has_job_offer = profile.get("job_offer", False)
    has_pnp       = profile.get("has_provincial_nomination", False)
    min_clb = min(
        profile.get("clb_speaking", 0),
        profile.get("clb_listening", 0),
        profile.get("clb_reading", 0),
        profile.get("clb_writing", 0),
    )

    # Pathway 1: 1+ year skilled foreign experience in NOC 0/A/B
    skilled_foreign = foreign_years >= 1 and foreign_noc in ["0", "A", "B"]

    # Pathway 2: Valid job offer
    # Pathway 3: Provincial nomination
    if not skilled_foreign and not has_job_offer and not has_pnp:
        return False, (
            "Requires at least 1 year of skilled foreign work experience (NOC 0, A, or B), "
            "a valid job offer, or a provincial nomination."
        )

    # Language minimum: CLB 7+ in all abilities (unless job offer exempts)
    if not has_job_offer and min_clb < 7:
        return False, (
            f"Requires CLB 7+ in all language abilities — your minimum is CLB {min_clb}."
        )

    return True, "Meets minimum FSW requirements."


def calculate_fsw(profile):
    """
    Run the full FSW 67-point grid.
    Returns score, breakdown, and eligibility.
    """
    meets_min, min_reason = check_fsw_minimum_requirements(profile)

    if not meets_min:
        return {
            "eligible": False,
            "stream": "Federal Skilled Worker (FSW)",
            "reasons": [min_reason],
            "grid_score": None,
            "breakdown": None,
        }

    # All CLB scores: first language + second language (if available)
    first_clbs = [
        profile.get("clb_speaking", 0),
        profile.get("clb_listening", 0),
        profile.get("clb_reading", 0),
        profile.get("clb_writing", 0),
    ]
    french_clbs = profile.get("french_clb_scores", [])
    all_clbs = first_clbs + french_clbs

    total_years = (
        profile.get("canadian_work_years", 0) +
        profile.get("foreign_work_years", 0)
    )

    language     = get_fsw_language_points(all_clbs)
    education    = get_fsw_education_points(profile.get("education", ""))
    experience   = get_fsw_experience_points(total_years)
    age          = get_fsw_age_points(profile.get("age", 0))
    employment   = get_fsw_arranged_employment_points(profile.get("job_offer", False))
    adaptability = get_fsw_adaptability_points(profile)

    grid_score = language + education + experience + age + employment + adaptability
    eligible = grid_score >= 67

    reasons = []
    if eligible:
        reasons.append(f"FSW grid score is {grid_score}/100 — meets the 67-point minimum.")
    else:
        reasons.append(
            f"FSW grid score is {grid_score}/100 — below the 67-point minimum needed."
        )

    return {
        "eligible": eligible,
        "stream": "Federal Skilled Worker (FSW)",
        "reasons": reasons,
        "grid_score": grid_score,
        "breakdown": {
            "language":     language,
            "education":    education,
            "experience":   experience,
            "age":          age,
            "employment":   employment,
            "adaptability": adaptability,
        },
    }