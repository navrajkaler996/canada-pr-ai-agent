# advice_engine.py
# Hard-coded advice logic. No AI judgment

CATEGORY_LABELS = {
    "stem": "STEM Occupations",
    "healthcare": "Healthcare & Social Services",
    "education": "Education Occupations",
    "trades": "Skilled Trades",
    "transport": "Transportation Occupations",
    "agriculture": "Agriculture & Food Production",
    "business": "Business & Management",
}

def generate_advice(immigration_status, work_permit_expiry, eligibility, draws, simulations, crs_score, category_draw=None, occupation_category=None):

    warnings = []
    stream_summaries = []
    top_improvements = []
    follow_up_question = None

    # ── Stream analysis ───────────────────────────────────────────────────────

    if immigration_status == "study_permit":
        relevant_streams = []
    elif immigration_status == "work_permit":
        relevant_streams = [
            ("CEC",    "Canadian Experience Class"),
            ("French", "French-Language Category"),
        ]
    else:  # outside_canada or other
        relevant_streams = [
            ("FSW",    "Federal Skilled Worker"),
            ("FST",    "Federal Skilled Trades"),
            ("French", "French-Language Category"),
        ]

    fsw_warning_added = False
    fsw_eligible = eligibility.get("FSW", {}).get("eligible", False)
    fsw_not_eligible = not fsw_eligible

    for stream_key, label in relevant_streams:
        elig = eligibility.get(stream_key, {})
        draw = draws.get(stream_key) if draws else None

        if not elig.get("eligible"):
            continue

        if not draw or draw.get("error"):
            # Only add FSW warning once
            if stream_key == "FSW" and not fsw_warning_added:
                warnings.append(f"{label} has had no draws in the last 2 years — do not wait for this stream.")
                fsw_warning_added = True
            continue

        pct = draw["percentage"]
        qualifying = draw["qualifying_draws"]
        total = draw["total_draws"]

        if pct == 0:
            stream_summaries.append(
                f"{label}: Your score of {crs_score} has not met the cutoff in any of the {total} draws in the last 2 years. "
                f"The lowest cutoff was {draw['lowest_cutoff']}."
            )
        elif pct < 25:
            stream_summaries.append(
                f"{label}: Your score qualified in only {qualifying} of {total} draws ({pct}%). "
                f"Cutoffs ranged from {draw['lowest_cutoff']} to {draw['highest_cutoff']}."
            )
        elif pct < 60:
            stream_summaries.append(
                f"{label}: Your score qualified in {qualifying} of {total} draws ({pct}%). "
                f"You are a moderate candidate — score improvement would significantly increase your chances."
            )
        else:
            stream_summaries.append(
                f"{label}: Your score qualified in {qualifying} of {total} draws ({pct}%). "
                f"You are a strong candidate for this stream."
            )

    # ── Category draw analysis ────────────────────────────────────────────────

    has_strong_category = False
    has_any_category = False
    cat_label = None

    if category_draw and not category_draw.get("error"):
        has_any_category = True
        cat_key = category_draw.get("category")
        cat_label = CATEGORY_LABELS.get(cat_key, cat_key)
        pct = category_draw["percentage"]
        qualifying = category_draw["qualifying_draws"]
        total = category_draw["total_draws"]
        last_cutoff = category_draw["last_draw_cutoff"]
        last_date = category_draw["last_draw_date"]

        if pct >= 60:
            has_strong_category = True
            stream_summaries.insert(0,
                f"{cat_label} category draws: Your score qualified in {qualifying} of {total} draws ({pct}%) "
                f"in the last 2 years. The last draw cutoff was {last_cutoff} on {last_date}. "
                f"You are a strong candidate — focus on entering the Express Entry pool and applying."
            )
        elif pct >= 25:
            stream_summaries.insert(0,
                f"{cat_label} category draws: Your score qualified in {qualifying} of {total} draws ({pct}%) "
                f"in the last 2 years. The last draw cutoff was {last_cutoff} on {last_date}. "
                f"You are a moderate candidate — improving your score would significantly increase your chances."
            )
        else:
            stream_summaries.insert(0,
                f"{cat_label} category draws: Your score has not been competitive in recent draws ({pct}% qualifying rate). "
                f"The last draw cutoff was {last_cutoff} on {last_date}. "
                f"Improving your score could increase your chances in future {cat_label} draws significantly."
            )

    # ── Detect inactive category (occupation selected but no draws in last 2 years) ──
    # e.g. user works in STEM but last STEM draw was over 2 years ago
    category_inactive = occupation_category is not None and not has_any_category
    inactive_cat_label = CATEGORY_LABELS.get(occupation_category, occupation_category) if occupation_category else None

    # ── User-type specific warnings ───────────────────────────────────────────

    if immigration_status == "outside_canada":

        # Case 3 — Not eligible for FSW (must check first)
        if fsw_not_eligible:
            fsw_elig = eligibility.get("FSW", {})
            fsw_reason = fsw_elig.get("reasons", [""])[0] if fsw_elig.get("reasons") else ""

            if has_any_category:
                warnings.append(
                    f"You are not currently eligible for Federal Skilled Worker. {fsw_reason} "
                    f"You need FSW eligibility to enter the Express Entry pool."
                )
                warnings.append(
                    f"However, your occupation is in the {cat_label} category which IRCC actively draws from. "
                    f"Once you meet the FSW minimum, improving your CRS score could make you competitive in {cat_label} draws."
                )
                warnings.append(
                    "Alternatively, a study permit would give you Canadian education and work experience, "
                    "bypassing the FSW requirement entirely by making you eligible for CEC."
                )
            else:
                warnings.append(
                    f"You are not currently eligible for Federal Skilled Worker. {fsw_reason} "
                    f"Focus on meeting the FSW eligibility requirements first."
                )
                warnings.append(
                    "Alternatively, coming to Canada on a study permit is a strong pathway — "
                    "it gives you Canadian education, PGWP work authorization, and CEC eligibility after 1 year of skilled work."
                )

        # Case 1 — FSW eligible + strong category score
        elif has_strong_category:
            warnings.append(
                "You have a real opportunity through category-based Express Entry draws. "
                "Create an Express Entry profile and enter the pool as soon as possible."
            )
            warnings.append(
                "A study permit is an alternative if you want to further improve your score, "
                "but it is not your only option given your category draw competitiveness."
            )

        # Case 1b — FSW eligible + active category but score not competitive
        elif has_any_category:
            warnings.append(
                f"Your occupation is in a category that IRCC actively draws from ({cat_label}). "
                f"Improving your score is your most direct path to an ITA through category-based draws."
            )
            warnings.append(
                "Alternatively, coming to Canada on a study permit lets you gain Canadian education "
                "and work experience on a PGWP, which would significantly boost your score and make you eligible for CEC."
            )

        # Case 2a — FSW eligible, category exists but no recent draws
        elif fsw_eligible and fsw_warning_added and category_inactive:
            warnings.append(
                f"Your occupation falls under the {inactive_cat_label} category, which IRCC has drawn from in the past. "
                f"However, there have been no {inactive_cat_label} draws in the last 2 years. "
                f"Monitor IRCC announcements closely — if this category reopens, you may be competitive."
            )
            warnings.append(
                "In the meantime, focus on improving your score to stay competitive if category draws resume. "
                "A study permit is also an option to gain Canadian experience and become eligible for CEC."
            )
            warnings.append(
                "Learning French to CLB 7+ could also significantly boost your score "
                "and open the French-language category draws."
            )

        # Case 2b — FSW eligible but no category match and FSW has no draws
        elif fsw_eligible and fsw_warning_added:
            warnings.append(
                "Since FSW draws have been inactive, consider two alternative strategies:"
            )
            warnings.append(
                "1. Gain experience in a targeted occupation such as healthcare, education, or trades "
                "in your home country — these categories have active IRCC draws with lower cutoffs."
            )
            warnings.append(
                "2. Come to Canada on a study permit to gain Canadian education and work experience on a PGWP, "
                "which would make you eligible for CEC."
            )
            warnings.append(
                "Learning French to CLB 7+ could add significant points "
                "and open the French-language category draws."
            )

        # Fallback
        else:
            warnings.append(
                "Finding a job in Canada from abroad is extremely difficult. "
                "Do not rely on a job offer as a strategy unless you have an existing employer relationship."
            )

    elif immigration_status == "study_permit":
        pct = draws.get("CEC", {}).get("percentage", 0) if draws and draws.get("CEC") else 0
        qualifying = draws.get("CEC", {}).get("qualifying_draws", 0) if draws and draws.get("CEC") else 0
        total = draws.get("CEC", {}).get("total_draws", 0) if draws and draws.get("CEC") else 0

        if draws and draws.get("CEC") and not draws["CEC"].get("error"):
            stream_summaries.append(
                f"Your projected score of {crs_score} would have qualified in {qualifying} of {total} "
                f"CEC draws ({pct}%) in the last 2 years."
            )

        warnings.append(
            "You are currently on a study permit with no Canadian work experience — that is expected at this stage. "
            "Once you graduate and complete 1 year of skilled work in NOC 0, A, or B, "
            "you will be eligible for CEC."
        )

    elif immigration_status == "work_permit":
        if work_permit_expiry == "less_than_6":
            warnings.append(
                "URGENT: You have less than 6 months left on your work permit. "
                "Apply to PNP streams immediately. "
                "Talk to your employer about a bridging open work permit or LMIA-based extension. "
                "Do not rely on improvements that take more than a few months."
            )
        elif work_permit_expiry == "6_to_12":
            warnings.append(
                "You have 6–12 months left on your work permit. "
                "Focus on PNP streams available now and consider retaking your language test "
                "if you are close to a CLB improvement. Talk to your employer about extension options."
            )

    # ── Filter simulations by realism ─────────────────────────────────────────

    time_constrained = (
        immigration_status == "work_permit" and
        work_permit_expiry in ["less_than_6", "6_to_12"]
    )

    excluded_if_outside_canada = [
        "one_more_canadian_work_year",
        "canadian_education_1yr",
        "canadian_education_3yr",
    ]

    excluded_if_study_permit = [
        "one_more_canadian_work_year",
        "add_french_clb7",
        "add_french_clb9",
        "canadian_education_1yr",
        "canadian_education_3yr",
    ]

    excluded_if_time_constrained = [
        "one_more_canadian_work_year",
        "canadian_education_1yr",
        "canadian_education_3yr",
    ]

    sims = simulations.get("simulations", {})
    for key, sim in sims.items():
        if immigration_status == "outside_canada" and key in excluded_if_outside_canada:
            continue
        if immigration_status == "study_permit" and key in excluded_if_study_permit:
            continue
        if time_constrained and key in excluded_if_time_constrained:
            continue
        top_improvements.append({
            "key": key,
            "description": sim["description"],
            "delta": sim["delta"],
            "new_score": sim["new_score"],
        })

    top_improvements = top_improvements[:3]

    # ── Follow-up question by user type ───────────────────────────────────────

    if immigration_status == "outside_canada":
        if has_strong_category:
            follow_up_question = "Would you like to know what steps to take to create your Express Entry profile?"
        elif has_any_category:
            follow_up_question = "Would you like to know how many points you need to be competitive in your category draws?"
        elif category_inactive:
            follow_up_question = f"Would you like to monitor when {inactive_cat_label} draws might resume?"
        elif fsw_not_eligible:
            follow_up_question = "Would you like to know what you need to do to become eligible for Federal Skilled Worker?"
        else:
            follow_up_question = "Are you considering coming to Canada on a study permit, or do you have any ties to a specific province?"
    elif immigration_status == "study_permit":
        follow_up_question = "What are you studying and when do you expect to graduate?"
    elif immigration_status == "work_permit":
        if work_permit_expiry == "less_than_6":
            follow_up_question = "Is your employer willing to support a work permit extension or have you looked into a bridging open work permit?"
        else:
            follow_up_question = "Is your employer supportive of your PR journey, and have you looked into any provincial nominee programs in your province?"
    else:
        follow_up_question = "Do you have any ties to a specific Canadian province that might open up PNP pathways?"

    return {
        "stream_summaries": stream_summaries,
        "warnings": warnings,
        "top_improvements": top_improvements,
        "follow_up_question": follow_up_question,
    }