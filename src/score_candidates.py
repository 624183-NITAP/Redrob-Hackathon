def score_candidate(features):

    score = 0

    # Experience fit (JD prefers roughly 5–9 years)

    years = features["years"]

    if 5 <= years <= 9:
        score += 25
    elif 4 <= years <= 10:
        score += 15
    else:
        score += 5


    # Relevant title

    if features["title_match"]:
        score += 30


    # Bad-title penalty

    if features["bad_title"]:
        score -= 25


    # AI skill score

    score += min(
        features["ai_skill_count"]*5,
        25
    )

    return score