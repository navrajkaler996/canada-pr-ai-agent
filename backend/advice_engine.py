# advice_engine.py
# Hard-coded advice logic. No AI judgment 

def generate_advice(immigration_status, work_permit_expiry, eligibility, draws, simulations, crs_score):

    warnings = []
    stream_summaries = []
    top_improvements = []
    follow_up_question = None

    #  Stream analysis — filtered by user type 

    # Which streams are relevant per user type
    if immigration_status == "study_permit":
        relevant_streams = []  # no current eligible streams expected — skip loop entirely
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

    for stream_key, label in relevant_streams:
        elig = eligibility.get(stream_key, {})
        draw = draws.get(stream_key)

        if not elig.get("eligible"):
            continue

        if not draw or draw.get("error"):
            warnings.append(f"{label} has had no draws in the last 2 years — do not wait for this stream.")
            if stream_key == "FSW":
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

    #  User-type specific warnings 

    if immigration_status == "outside_canada":
        # Only add CEC warning if FSW warning didn't already cover the "no path" message
        if not fsw_warning_added:
            warnings.append(
                "You are outside Canada and not currently eligible for CEC. "
                "FSW is your primary stream — focus on improving your score for the next draw."
            )
        else:
            warnings.append(
                "The most realistic pathway to Canada is a study permit. "
                "This lets you gain Canadian education, work experience on a PGWP, and become eligible for CEC."
            )
        warnings.append(
            "Finding a job in Canada from abroad is extremely difficult. "
            "Do not rely on a job offer as a strategy unless you have an existing employer relationship."
        )

    elif immigration_status == "study_permit":
        pct = draws.get("CEC", {}).get("percentage", 0) if draws.get("CEC") else 0
        qualifying = draws.get("CEC", {}).get("qualifying_draws", 0) if draws.get("CEC") else 0
        total = draws.get("CEC", {}).get("total_draws", 0) if draws.get("CEC") else 0

        if draws.get("CEC") and not draws["CEC"].get("error"):
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

    #  Filter simulations by realism 

    time_constrained = (
        immigration_status == "work_permit" and
        work_permit_expiry in ["less_than_6", "6_to_12"]
    )

    # For study permit users, exclude Canadian work year simulation — they can't do that yet
    excluded_if_study_permit = ["one_more_canadian_work_year",    "add_french_clb7",
    "add_french_clb9",
    "canadian_education_1yr",
    "canadian_education_3yr",]
    excluded_if_time_constrained = ["one_more_canadian_work_year", "canadian_education_1yr", "canadian_education_3yr"]

    sims = simulations.get("simulations", {})
    for key, sim in sims.items():
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

    #  Follow-up question by user type 

    if immigration_status == "outside_canada":
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