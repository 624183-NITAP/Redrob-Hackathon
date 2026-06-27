import json
import csv
import math

# ======================
# Load candidates
# ======================

candidates = []

with open("data/candidates.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            candidates.append(json.loads(line))

print("Loaded:", len(candidates))

# ======================
# Scoring
# ======================

def score_candidate(c):

    raw_score = 0.0

    profile = c.get("profile", {})
    signals = c.get("redrob_signals", {})

    title = profile.get("current_title", "").lower()
    years = profile.get("years_of_experience", 0)
    career = c.get("career_history", [])

    # ==================
    # Skill scoring
    # ==================

    retrieval_terms = {
        "rag",
        "retrieval",
        "ranking",
        "search",
        "recommendation",
        "bm25",
        "faiss",
        "milvus",
        "pinecone",
        "weaviate",
        "qdrant",
        "elasticsearch",
        "embeddings",
        "vector db",
        "sentence transformers"
    }

    ml_terms = {
        "machine learning",
        "deep learning",
        "nlp",
        "llm",
        "transformers",
        "pytorch",
        "tensorflow",
        "lora"
    }

    vector_terms = {
        "faiss",
        "milvus",
        "pinecone",
        "weaviate",
        "qdrant"
    }

    matched = 0.0

    skill_names = []

    for skill in c.get("skills", []):

        name = skill.get("name", "").lower()
        skill_names.append(name)

        duration = skill.get("duration_months", 0)
        endorsements = skill.get("endorsements", 0)

        trust = 1.0

        if duration < 6:
            trust *= 0.5

        if endorsements < 3:
            trust *= 0.7

        if any(term in name for term in retrieval_terms):
            matched += 3 * trust

        elif any(term in name for term in ml_terms):
            matched += 2 * trust

        # Extra vector DB bonus
        if any(v in name for v in vector_terms):
            matched += 2 * trust

    skill_score = matched * 2.0
    raw_score += skill_score

    # ==================
    # RAG + Vector DB synergy
    # ==================

    has_rag = any("rag" in s for s in skill_names)

    has_vector = any(
        v in s
        for s in skill_names
        for v in vector_terms
    )

    if has_rag and has_vector:
        raw_score += 10

    # ==================
    # Experience
    # ==================

    if 4 <= years <= 8:
        raw_score += 20

    elif 3 <= years < 4:
        raw_score += 12

    elif years > 8:
        raw_score += 10

    # ==================
    # Title relevance
    # ==================

    strong_titles = [
        "search engineer",
        "recommendation systems engineer",
        "ranking engineer",
        "ai research engineer",
        "machine learning engineer",
        "ml engineer",
        "applied ml engineer"
    ]

    medium_titles = [
        "data scientist",
        "nlp engineer",
        "ai engineer",
        "research engineer"
    ]

    bad_titles = [
        "customer support",
        "civil engineer",
        "mechanical engineer",
        "operations manager",
        "business analyst",
        "marketing",
        "sales",
        "accountant",
        "graphic designer",
        "content writer",
        "hr"
    ]

    if any(t in title for t in strong_titles):
        raw_score += 30

    elif any(t in title for t in medium_titles):
        raw_score += 15

    if any(t in title for t in bad_titles):
        raw_score -= 40

    # ==================
    # Retrieval title bonus
    # ==================

    if "search engineer" in title:
        raw_score += 15

    if "recommendation" in title:
        raw_score += 12

    if "ranking" in title:
        raw_score += 10

    if "applied ml" in title:
        raw_score += 5

    if "senior" in title:
        raw_score += 5

    if "staff" in title:
        raw_score += 8

    if "lead" in title:
        raw_score += 6

    if "research" in title:
        raw_score -= 1

    # Junior title penalty
    if "junior" in title and years > 5:
        raw_score -= 20

    # ==================
    # Company bonus
    # ==================

    service_companies = {
        "tcs",
        "infosys",
        "wipro",
        "accenture",
        "mindtree",
        "cognizant"
    }

    product_bonus = 0

    for job in career:

        company = job.get("company", "").lower()

        if any(sc in company for sc in service_companies):
            product_bonus -= 2
        else:
            product_bonus += 1

    raw_score += product_bonus

    # ==================
    # Behavioral signals
    # ==================

    raw_score += signals.get(
        "recruiter_response_rate", 0
    ) * 8

    raw_score += signals.get(
        "interview_completion_rate", 0
    ) * 8

    raw_score += signals.get(
        "github_activity_score", 0
    ) / 6

    if signals.get("open_to_work_flag", False):
        raw_score += 5

    if signals.get("notice_period_days", 0) > 90:
        raw_score -= 10

    response_time = signals.get(
        "avg_response_time_hours",
        999
    )

    if response_time < 24:
        raw_score += 3

    elif response_time > 100:
        raw_score -= 3

    # ==================
    # Recruiter activity
    # ==================

    raw_score += min(
        signals.get(
            "saved_by_recruiters_30d",
            0
        ),
        15
    )

    # ==================
    # Suspicious detection
    # ==================

    suspicious = 0

    for skill in c.get("skills", []):

        prof = skill.get(
            "proficiency",
            ""
        ).lower()

        duration = skill.get(
            "duration_months",
            0
        )

        if prof == "advanced" and duration < 6:
            suspicious += 1

    if years > 8 and len(career) <= 1:
        suspicious += 1

    if suspicious >= 3:
        raw_score -= 25

    # ==================
    # Safety check
    # ==================

    if math.isnan(raw_score) or math.isinf(raw_score):
        raw_score = 0.0

    return round(raw_score, 2)

# ======================
# Reasoning
# ======================

def get_reason(c, score):

    p = c.get("profile", {})

    title = p.get("current_title", "")
    years = p.get("years_of_experience", 0)

    skills = [
        s.get("name", "")
        for s in c.get("skills", [])
    ]

    keywords = [
        "RAG",
        "FAISS",
        "Milvus",
        "PyTorch",
        "NLP",
        "Machine Learning"
    ]

    skill_lower = [x.lower() for x in skills]

    important = [
        k for k in keywords
        if k.lower() in skill_lower
    ]

    text = f"{title} with {years:.1f} years experience"

    if important:
        text += "; key skills: " + ", ".join(important[:3])

    return text

# ======================
# Rank
# ======================

ranked = []

for c in candidates:
    s = score_candidate(c)
    ranked.append((s, c))

ranked.sort(
    key=lambda x: x[0],
    reverse=True
)

top100 = ranked[:100]

# ======================
# Save CSV
# ======================

with open(
    "team_sairam.csv",
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "candidate_id",
        "rank",
        "score",
        "reasoning"
    ])

    for rank, (score, c) in enumerate(top100, 1):

        writer.writerow([
            c.get("candidate_id"),
            rank,
            score,
            get_reason(c, score)
        ])

print("team_sairam.csv created successfully")