# rag/retriever.py

from rag.embeddings import embedding_model
from rag.vector_store import collection


# --------------------------------------------------
# WEIGHT CONFIGURATION
# --------------------------------------------------

ROLE_WEIGHT = 0.6
SENIORITY_WEIGHT = 0.25
SKILLS_WEIGHT = 0.15


# --------------------------------------------------
# SENIORITY SCORING
# --------------------------------------------------

def compute_seniority_score(
    query,
    metadata
):

    query = query.lower()

    seniority_keywords = {

        "entry":[
            "entry",
            "graduate",
            "junior",
            "fresher",
            "campus"
        ],

        "mid":[
            "mid",
            "manager",
            "experienced"
        ],

        "senior":[
            "senior",
            "director",
            "executive",
            "leadership",
            "cxo",
            "vp"
        ]
    }

    metadata_text = str(metadata).lower()

    score = 0.5

    for level,keywords in seniority_keywords.items():

        query_match = any(
            k in query
            for k in keywords
        )

        metadata_match = any(
            k in metadata_text
            for k in keywords
        )

        if query_match and metadata_match:

            score += 0.3

    return min(score,1.0)


# --------------------------------------------------
# SKILLS SCORE
# --------------------------------------------------

def compute_skills_score(
    query,
    metadata
):

    query_words = set(
        query.lower().split()
    )

    metadata_words = set(
        str(metadata)
        .lower()
        .split()
    )

    overlap = query_words.intersection(
        metadata_words
    )

    if not query_words:
        return 0.0

    return len(overlap)/len(query_words)


# --------------------------------------------------
# FINAL SCORE
# --------------------------------------------------

def compute_final_score(

    role_score,
    seniority_score,
    skills_score

):

    return (

        ROLE_WEIGHT*role_score
        + SENIORITY_WEIGHT*seniority_score
        + SKILLS_WEIGHT*skills_score

    )


# --------------------------------------------------
# MAIN RETRIEVAL
# --------------------------------------------------

def retrieve_assessments(

    query,
    state=None,
    top_k=5

):

    print(
        "RETRIEVAL START",
        flush=True
    )

    try:

        print(
            "Creating embedding",
            flush=True
        )

        query_embedding = (
            embedding_model
            .encode(query)
            .tolist()
        )

        print(
            "Embedding created",
            flush=True
        )

        print(
            "Testing collection",
            flush=True
        )

        print(
            f"Collection count: {collection.count()}",
            flush=True
        )

        return [

            {
                "name":"DEBUG TEST",

                "url":"test",

                "test_type":"Assessment",

                "description":"temporary",

                "scores":{
                    "final_score":1
                }
            }

        ]

    except Exception as e:

        print(
            "RETRIEVAL ERROR:",
            str(e),
            flush=True
        )

        return []


    try:

        retrieved_docs=results["documents"][0]

        metadatas=results["metadatas"][0]

        distances=results["distances"][0]

    except Exception as e:

        print(
            "RESULT PARSING ERROR:",
            str(e),
            flush=True
        )

        return []


    ranked_results=[]

    for doc,metadata,distance in zip(

        retrieved_docs,
        metadatas,
        distances

    ):

        role_score=(1-distance)

        seniority_score=compute_seniority_score(
            query,
            metadata
        )

        skills_score=compute_skills_score(
            query,
            metadata
        )

        final_score=compute_final_score(

            role_score,
            seniority_score,
            skills_score

        )

        ranked_results.append({

            "name":
            metadata.get(
                "name",
                ""
            ),

            "url":
            metadata.get(
                "url",
                ""
            ),

            "test_type":
            metadata.get(
                "test_type"
            )
            or metadata.get(
                "category"
            )
            or "Assessment",

            "description":
            doc,

            "scores":{

                "role_score":
                round(
                    role_score,
                    3
                ),

                "seniority_score":
                round(
                    seniority_score,
                    3
                ),

                "skills_score":
                round(
                    skills_score,
                    3
                ),

                "final_score":
                round(
                    final_score,
                    3
                )
            }

        })


    ranked_results=sorted(

        ranked_results,

        key=lambda x:
        x["scores"]["final_score"],

        reverse=True

    )

    print(
        f"Returning {len(ranked_results)} results",
        flush=True
    )

    return ranked_results[:top_k]