# rag/comparison.py


from rag.vector_store import collection


# --------------------------------------------------
# RETRIEVE SPECIFIC ASSESSMENTS FOR COMPARISON
# Uses fuzzy substring matching so partial names
# like "opq" still match "OPQ32r" in the catalog
# --------------------------------------------------

def retrieve_specific_assessments(names):

    results = []

    seen = set()

    catalog = collection.get(
        include=["metadatas"]
    )

    for metadata in catalog["metadatas"]:

        title = metadata.get(
            "name",
            ""
        ).lower()

        for name in names:

            # clean fragment — strip whitespace,
            # skip anything too short to be meaningful
            name_clean = name.strip().lower()

            if len(name_clean) < 3:
                continue

            if name_clean in title:

                assessment_name = metadata.get(
                    "name",
                    ""
                )

                # deduplicate
                if assessment_name in seen:
                    continue

                seen.add(assessment_name)

                results.append({
                    "name": assessment_name,
                    "url": metadata.get(
                        "url",
                        ""
                    ),
                    "test_type": (
                        metadata.get("test_type")
                        or metadata.get("category")
                        or "Assessment"
                    ),
                    "description": metadata.get(
                        "description",
                        ""
                    )
                })

    return results