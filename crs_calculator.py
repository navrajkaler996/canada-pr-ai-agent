#Calculate age points

def get_age_points(age, has_spouse):
    if has_spouse:
        age_points = {
            17: 0, 18: 90, 19: 95,
            30: 95, 31: 90, 32: 85, 33: 80, 34: 75,
            35: 70, 36: 65, 37: 60, 38: 55, 39: 50,
            40: 45, 41: 35, 42: 25, 43: 15, 44: 5
        }
    else:
        age_points = {
            17: 0, 18: 99, 19: 105,
            30: 105, 31: 99, 32: 94, 33: 88, 34: 83,
            35: 77, 36: 72, 37: 66, 38: 61, 39: 55,
            40: 50, 41: 39, 42: 28, 43: 17, 44: 6
        }

    if 20 <= age <= 29:
        return 100 if has_spouse else 110
    elif age >= 45:
        return 0
    else:
        return age_points.get(age, 0)

# calculate language points
def get_education_points(education_level, has_spouse):
    with_spouse = {
        "less_than_high_school": 0,
        "high_school": 28,
        "one_year": 84,
        "two_year": 91,
        "bachelors": 112,
        "two_or_more": 119,
        "masters": 126,
        "phd": 140
    }
    
    without_spouse = {
        "less_than_high_school": 0,
        "high_school": 30,
        "one_year": 90,
        "two_year": 98,
        "bachelors": 120,
        "two_or_more": 128,
        "masters": 135,
        "phd": 150
    }
    
    points = with_spouse if has_spouse else without_spouse
    return points.get(education_level, 0)

# calculate first langauge points
def get_first_language_points(clb_speaking, clb_listening, clb_reading, clb_writing, has_spouse):
    
    def clb_to_points(clb, has_spouse):
        if has_spouse:
            clb_points = {4: 6, 5: 6, 6: 8, 7: 16, 8: 22, 9: 29, 10: 32}
        else:
            clb_points = {4: 6, 5: 6, 6: 9, 7: 17, 8: 23, 9: 31, 10: 34}
        
        if clb < 4:
            return 0
        elif clb >= 10:
            return 32 if has_spouse else 34
        else:
            return clb_points.get(clb, 0)
    
    total = 0
    for clb in [clb_speaking, clb_listening, clb_reading, clb_writing]:
        total += clb_to_points(clb, has_spouse)
    
    return total

# calculate second langauge points
def get_second_language_points(clb_speaking, clb_listening, clb_reading, clb_writing, has_spouse):
    
    def clb_to_points(clb):
        if clb <= 4:
            return 0
        elif clb <= 6:
            return 1
        elif clb <= 8:
            return 3
        else:
            return 6
    
    total = 0
    for clb in [clb_speaking, clb_listening, clb_reading, clb_writing]:
        total += clb_to_points(clb)
    
    max_points = 22 if has_spouse else 24
    return min(total, max_points)


# calculate canadian work points
def get_canadian_work_experience_points(years, has_spouse):
    with_spouse = {0: 0, 1: 35, 2: 46, 3: 56, 4: 63, 5: 70}
    without_spouse = {0: 0, 1: 40, 2: 53, 3: 64, 4: 72, 5: 80}
    
    points = with_spouse if has_spouse else without_spouse
    
    if years >= 5:
        return 70 if has_spouse else 80
    else:
        return points.get(years, 0)

# calculate spouse education points
def get_spouse_education_points(education_level):
    points = {
        "less_than_high_school": 0,
        "high_school": 2,
        "one_year": 6,
        "two_year": 7,
        "bachelors": 8,
        "two_or_more": 9,
        "masters": 10,
        "phd": 10
    }
    return points.get(education_level, 0)

# calculate spouse language points
def get_spouse_language_points(clb_speaking, clb_listening, clb_reading, clb_writing):
    
    def clb_to_points(clb):
        if clb <= 4:
            return 0
        elif clb <= 6:
            return 1
        elif clb <= 8:
            return 3
        else:
            return 5
    
    total = 0
    for clb in [clb_speaking, clb_listening, clb_reading, clb_writing]:
        total += clb_to_points(clb)
    
    return total

# calculate spouse work points
def get_spouse_work_experience_points(years):
    points = {0: 0, 1: 5, 2: 7, 3: 8, 4: 9}
    
    if years >= 5:
        return 10
    else:
        return points.get(years, 0)


def get_skill_transferability_points(education_level, clb_scores, canadian_work_years, foreign_work_years, has_certificate):
    
    # helper - check minimum clb across all 4 abilities
    min_clb = min(clb_scores)
    all_clb_9_plus = min_clb >= 9
    all_clb_7_plus = min_clb >= 7
    all_clb_5_plus = min_clb >= 5

    # education levels that qualify as post secondary
    post_secondary_one_year = education_level in ["one_year", "two_year", "bachelors", "two_or_more", "masters", "phd"]
    post_secondary_three_plus = education_level in ["two_or_more", "masters", "phd", "bachelors"]
    masters_or_phd = education_level in ["masters", "phd"]

    def get_education_language_points():
        if not post_secondary_one_year:
            return 0
        if masters_or_phd or post_secondary_three_plus:
            if all_clb_9_plus:
                return 50
            elif all_clb_7_plus:
                return 25
        elif post_secondary_one_year:
            if all_clb_9_plus:
                return 25
            elif all_clb_7_plus:
                return 13
        return 0

    def get_education_canadian_work_points():
        if not post_secondary_one_year:
            return 0
        if masters_or_phd or post_secondary_three_plus:
            if canadian_work_years >= 2:
                return 50
            elif canadian_work_years >= 1:
                return 25
        elif post_secondary_one_year:
            if canadian_work_years >= 2:
                return 25
            elif canadian_work_years >= 1:
                return 13
        return 0

    def get_foreign_work_language_points():
        if foreign_work_years == 0:
            return 0
        if foreign_work_years >= 3:
            if all_clb_9_plus:
                return 50
            elif all_clb_7_plus:
                return 25
        else:  # 1 or 2 years
            if all_clb_9_plus:
                return 25
            elif all_clb_7_plus:
                return 13
        return 0

    def get_foreign_work_canadian_work_points():
        if foreign_work_years == 0:
            return 0
        if foreign_work_years >= 3:
            if canadian_work_years >= 2:
                return 50
            elif canadian_work_years >= 1:
                return 25
        else:  # 1 or 2 years
            if canadian_work_years >= 2:
                return 25
            elif canadian_work_years >= 1:
                return 13
        return 0

    def get_certificate_points():
        if not has_certificate:
            return 0
        if all_clb_7_plus:
            return 50
        elif all_clb_5_plus:
            return 25
        return 0

    # each sub-section capped at 50, total capped at 100
    education_points = min(50, max(get_education_language_points(), get_education_canadian_work_points()))
    foreign_work_points = min(50, max(get_foreign_work_language_points(), get_foreign_work_canadian_work_points()))
    certificate_points = min(50, get_certificate_points())

    total = min(100, education_points + foreign_work_points + certificate_points)
    return total


def get_additional_points(has_canadian_sibling, french_clb_scores, english_clb_scores, canadian_education_years, has_provincial_nomination):
    total = 0

    # sibling points
    if has_canadian_sibling:
        total += 15

    # french language points
    if french_clb_scores and min(french_clb_scores) >= 7:
        if english_clb_scores and min(english_clb_scores) >= 5:
            total += 50
        else:
            total += 25

    # canadian education points
    if canadian_education_years >= 3:
        total += 30
    elif canadian_education_years >= 1:
        total += 15

    # provincial nomination
    if has_provincial_nomination:
        total += 600

    return total


def calculate_crs(profile):
    has_spouse = profile["has_spouse"]

    # core points
    age = get_age_points(profile["age"], has_spouse)
    education = get_education_points(profile["education"], has_spouse)
    language = get_first_language_points(
        profile["clb_speaking"],
        profile["clb_listening"],
        profile["clb_reading"],
        profile["clb_writing"],
        has_spouse
    )
    second_language = 0
    if profile.get("french_clb_scores"):
        second_language = get_second_language_points(
            profile["french_clb_scores"][0],
            profile["french_clb_scores"][1],
            profile["french_clb_scores"][2],
            profile["french_clb_scores"][3],
            has_spouse
        )
    canadian_work = get_canadian_work_experience_points(profile["canadian_work_years"], has_spouse)

    # spouse points
    spouse = 0
    if has_spouse:
        spouse = (
            get_spouse_education_points(profile["spouse_education"]) +
            get_spouse_language_points(
                profile["spouse_clb_speaking"],
                profile["spouse_clb_listening"],
                profile["spouse_clb_reading"],
                profile["spouse_clb_writing"]
            ) +
            get_spouse_work_experience_points(profile["spouse_canadian_work_years"])
        )

    # skill transferability
    clb_scores = [profile["clb_speaking"], profile["clb_listening"], profile["clb_reading"], profile["clb_writing"]]
    transferability = get_skill_transferability_points(
        profile["education"],
        clb_scores,
        profile["canadian_work_years"],
        profile["foreign_work_years"],
        profile.get("has_certificate", False)
    )

    # additional points
    french_clb = profile.get("french_clb_scores", [])
    english_clb = clb_scores if profile.get("first_language") == "english" else []
    additional = get_additional_points(
        profile.get("has_canadian_sibling", False),
        french_clb,
        english_clb,
        profile.get("canadian_education_years", 0),
        profile.get("has_provincial_nomination", False)
    )

    total = age + education + language + second_language + canadian_work + spouse + transferability + additional

    return {
        "total": total,
        "breakdown": {
            "age": age,
            "education": education,
            "language": language,
            "second_language": second_language,
            "canadian_work": canadian_work,
            "spouse": spouse,
            "transferability": transferability,
            "additional": additional
        }
    }


# test for second langauge
# profile = {
#     "has_spouse": False,
#     "age": 29,
#     "education": "two_or_more",
#     "clb_speaking": 9,
#     "clb_listening": 10,
#     "clb_reading": 10,
#     "clb_writing": 10,
#     "canadian_work_years": 0,
#     "foreign_work_years": 3,
#     "first_language": "english",
#     "has_canadian_sibling": True,
#     "french_clb_scores": [7, 7, 7, 7],
#     "canadian_education_years": 1,
#     "has_provincial_nomination": False
# }

# test for spouse
# profile = {
#     "has_spouse": True,
#     "age": 29,
#     "education": "two_or_more",
#     "clb_speaking": 9,
#     "clb_listening": 10,
#     "clb_reading": 10,
#     "clb_writing": 10,
#     "canadian_work_years": 0,
#     "foreign_work_years": 3,
#     "first_language": "english",
#     "has_canadian_sibling": True,
#     "french_clb_scores": [],
#     "canadian_education_years": 1,
#     "has_provincial_nomination": False,
#     "spouse_education": "bachelors",
#     "spouse_clb_speaking": 10,
#     "spouse_clb_listening": 10,
#     "spouse_clb_reading": 10,
#     "spouse_clb_writing": 10,
#     "spouse_canadian_work_years": 0
# }


profile = {
    "has_spouse": False,
    "age": 29,
    "education": "two_or_more",
    "clb_speaking": 9,
    "clb_listening": 10,
    "clb_reading": 10,
    "clb_writing": 10,
    "canadian_work_years": 0,
    "foreign_work_years": 3,
    "first_language": "english",
    "has_canadian_sibling": True,
    "french_clb_scores": [],
    "canadian_education_years": 1,
    "has_provincial_nomination": False
}

result = calculate_crs(profile)
print(f"Total CRS Score: {result['total']}")
print(f"Breakdown: {result['breakdown']}")


