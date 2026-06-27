import json

# =========================
# Load candidates
# =========================

candidates = []

with open(
    "data/candidates.jsonl",
    "r",
    encoding="utf-8"
) as f:

    for line in f:
        if line.strip():
            candidates.append(
                json.loads(line)
            )

print("Loaded:", len(candidates))


# =========================
# Score function
# =========================

def score_candidate(c):

    score = 0

    profile = c["profile"]
    signals = c["redrob_signals"]

    title = profile.get(
        "current_title",""
    ).lower()

    years = profile.get(
        "years_of_experience",0
    )

    skills = [
        s["name"].lower()
        for s in c.get("skills",[])
    ]

    ai_skills = {
        "machine learning",
        "deep learning",
        "nlp",
        "llm",
        "fine-tuning llms",
        "tensorflow",
        "pytorch",
        "rag",
        "milvus",
        "transformers"
    }

    matched = len(
        set(skills).intersection(ai_skills)
    )

    good_titles = [
        "ai engineer",
        "ml engineer",
        "machine learning engineer",
        "data scientist",
        "nlp engineer",
        "research engineer"
    ]

    bad_titles = [
        "marketing",
        "accountant",
        "sales",
        "content writer",
        "hr"
    ]

    for t in good_titles:
        if t in title:
            score += 30

    for t in bad_titles:
        if t in title:
            score -= 20


    if 3 <= years <= 8:
        score += 20

    elif years > 8:
        score += 10


    score += matched * 5


    score += (
        signals.get(
            "recruiter_response_rate",
            0
        ) * 10
    )

    score += (
        signals.get(
            "interview_completion_rate",
            0
        ) * 10
    )


    if signals.get(
        "open_to_work_flag",
        False
    ):
        score += 5


    if signals.get(
        "notice_period_days",
        0
    ) > 90:

        score -= 10


    github = signals.get(
        "github_activity_score",
        -1
    )

    if github > 50:
        score += 10


    return score


# =========================
# Ranking
# =========================

ranked=[]

for c in candidates:

    score = score_candidate(c)

    ranked.append(
        (score,c)
    )


ranked.sort(
    reverse=True,
    key=lambda x:x[0]
)


print("\nTOP 10\n")

for i,(score,c) in enumerate(
    ranked[:10],
    1
):

    print(
        i,
        c["candidate_id"],
        c["profile"]["current_title"],
        score
    )