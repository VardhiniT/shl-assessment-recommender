from rag.vector_store import collection


def retrieve_specific_assessments(names):

    results = []

    catalog = collection.get(
        include=["metadatas"]
    )

    for metadata in catalog["metadatas"]:

        title = metadata.get(
            "name",
            ""
        ).lower()

        for name in names:

            name_clean = (
                name
                .strip()
                .lower()
            )

            if (
                len(name_clean) > 4
                and name_clean in title
            ):

                results.append({

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
                        metadata.get(
                            "description",
                            ""
                        )

                })

    return results