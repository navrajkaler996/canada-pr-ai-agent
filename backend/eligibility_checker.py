# eligibility_checker.py
# Checks which Express Entry streams a user is eligible for.
# Returns facts - no AI

from fsw_calculator import calculate_fsw

def check_cec(profile):
    """
    Canadian Experience Class eligibility.
    Requires:
    - 1+ year skilled Canadian work experience (NOC 0, A, or B) in last 3 years
    - CLB 7+ in all 4 abilities if NOC 0 or A
    - CLB 5+ in all 4 abilities if NOC B
    - Must not be planning to live in Quebec
    """
    reasons = []
    eligible = True

    canadian_years = profile.get("canadian_work_years", 0)
    noc = profile.get("canadian_noc", None)
    min_clb = min(
        profile.get("clb_speaking", 0),
        profile.get("clb_listening", 0),
        profile.get("clb_reading", 0),
        profile.get("clb_writing", 0),
    )

    # Check work experience
    if canadian_years < 1:
        eligible = False
        reasons.append("Requires at least 1 year of skilled Canadian work experience — you have none.")
    
    # Check NOC level
    if canadian_years >= 1:
        if noc in ["CD", None]:
            eligible = False
            reasons.append("Canadian experience must be in a skilled occupation (NOC 0, A, or B) — yours is NOC C/D or unknown.")
        elif noc in ["0", "A"]:
            if min_clb < 7:
                eligible = False
                reasons.append(f"NOC 0/A requires CLB 7+ in all abilities — your minimum CLB is {min_clb}.")
        elif noc == "B":
            if min_clb < 5:
                eligible = False
                reasons.append(f"NOC B requires CLB 5+ in all abilities — your minimum CLB is {min_clb}.")

    if eligible:
        reasons.append(
            f"{canadian_years} year(s) Canadian experience in NOC {noc}, CLB {min_clb} across all abilities."
        )

    return {
        "eligible": eligible,
        "stream": "Canadian Experience Class (CEC)",
        "reasons": reasons,
    }


def check_fst(profile):
    """
    Federal Skilled Trades eligibility.
    Requires:
    - Valid trade certificate (Red Seal or provincial)
    - CLB 5+ in speaking and listening
    - CLB 4+ in reading and writing
    - 2+ years of work experience in a skilled trade in last 5 years
      (Canadian or foreign)
    """
    reasons = []
    eligible = True

    has_certificate = profile.get("trade_certificate", False)
    clb_speaking  = profile.get("clb_speaking", 0)
    clb_listening = profile.get("clb_listening", 0)
    clb_reading   = profile.get("clb_reading", 0)
    clb_writing   = profile.get("clb_writing", 0)
    canadian_years = profile.get("canadian_work_years", 0)
    foreign_years  = profile.get("foreign_work_years", 0)
    total_trade_years = canadian_years + foreign_years

    # Check trade certificate
    if not has_certificate:
        eligible = False
        reasons.append("Requires a valid trade certificate (Red Seal or provincial) — you don't have one.")

    # Check language
    if clb_speaking < 5 or clb_listening < 5:
        eligible = False
        reasons.append(
            f"Requires CLB 5+ in speaking and listening — "
            f"your speaking is CLB {clb_speaking}, listening is CLB {clb_listening}."
        )
    if clb_reading < 4 or clb_writing < 4:
        eligible = False
        reasons.append(
            f"Requires CLB 4+ in reading and writing — "
            f"your reading is CLB {clb_reading}, writing is CLB {clb_writing}."
        )

    # Check work experience (2+ years in trades)
    if total_trade_years < 2:
        eligible = False
        reasons.append(
            f"Requires 2+ years of skilled trade work experience — "
            f"you have {total_trade_years} year(s) total."
        )

    if eligible:
        reasons.append(
            f"Valid trade certificate, CLB scores meet minimums, "
            f"{total_trade_years} year(s) of trade experience."
        )

    return {
        "eligible": eligible,
        "stream": "Federal Skilled Trades (FST)",
        "reasons": reasons,
    }


def check_french_category(profile):
    """
    French-language category draw eligibility.
    Requires:
    - NCLC 7+ in all four abilities (speaking, listening, reading, writing)
    - Must have taken TEF Canada or TCF Canada
    """
    reasons = []
    eligible = True

    french_clb = profile.get("french_clb_scores", [])
    first_language = profile.get("first_language", "")
    second_language_test = profile.get("second_language_test", "none")

    # Determine if French scores exist
    has_french_scores = (
        # French was their first language test
        first_language in ["french"] and len(french_clb) == 4
    ) or (
        # French was their second language test
        second_language_test in ["TEF", "TCF"] and len(french_clb) == 4
    )

    if not has_french_scores:
        eligible = False
        reasons.append("Requires TEF Canada or TCF Canada scores — no French test on file.")
    else:
        min_nclc = min(french_clb)
        if min_nclc < 7:
            eligible = False
            reasons.append(
                f"Requires NCLC 7+ in all four abilities — "
                f"your minimum French score is NCLC {min_nclc}."
            )
        else:
            reasons.append(f"NCLC {min_nclc}+ across all abilities — eligible for French category draws.")

    return {
        "eligible": eligible,
        "stream": "French-Language Category",
        "reasons": reasons,
    }


def check_eligibility(profile):
    """
    Run all eligibility checks and return results.
    """
    return {
        "CEC":    check_cec(profile),
        "FST":    check_fst(profile),
        "French": check_french_category(profile),
        "FSW":    calculate_fsw(profile),
    }