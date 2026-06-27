# Core AI/retrieval skills from JD

CORE_SKILLS = {
    "embeddings",
    "retrieval",
    "vector search",
    "pinecone",
    "milvus",
    "weaviate",
    "qdrant",
    "faiss",
    "elasticsearch",
    "opensearch",
    "llm",
    "fine-tuning llms",
    "lora",
    "qlora",
    "ranking",
    "bm25",
    "python",
    "nlp"
}


GOOD_TITLES = {
    "ai engineer",
    "machine learning engineer",
    "ml engineer",
    "senior machine learning engineer",
    "data scientist",
    "nlp engineer",
    "search engineer"
}


BAD_TITLES = {
    "marketing manager",
    "hr manager",
    "graphic designer",
    "content writer",
    "accountant",
    "sales executive"
}


def extract_features(candidate):

    profile = candidate["profile"]

    title = profile["current_title"].lower()

    skills = {
        s["name"].lower()
        for s in candidate["skills"]
    }

    years = profile["years_of_experience"]

    ai_skill_count = len(
        skills & CORE_SKILLS
    )

    title_match = int(
        title in GOOD_TITLES
    )

    bad_title = int(
        title in BAD_TITLES
    )

    return {
        "years": years,
        "title": title,
        "title_match": title_match,
        "bad_title": bad_title,
        "ai_skill_count": ai_skill_count
    }