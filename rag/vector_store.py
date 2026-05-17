import json
import chromadb

from rag.embeddings import embedding_model

# --------------------------------------------------
# CHROMA CONFIG
# --------------------------------------------------

CHROMA_PATH = "vector_db"

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_or_create_collection(
    name="shl_assessments"
)


# --------------------------------------------------
# CREATE VECTOR DB
# --------------------------------------------------

def create_vector_db():

    with open(
        "data/processed_assessments.json",
        "r"
    ) as f:

        data = json.load(f)

    documents = []
    embeddings = []
    metadatas = []
    ids = []

    for idx, item in enumerate(data):

        search_text = item[
            "search_text"
        ]

        embedding = (
            embedding_model
            .encode(search_text)
            .tolist()
        )

        documents.append(
            search_text
        )

        embeddings.append(
            embedding
        )

        metadatas.append({

            "name":
            item["name"],

            "url":
            item["url"],

            "test_type":
            item["test_type"],

            "duration":
            item["duration"],

            "remote_testing":
            item["remote_testing"]

        })

        ids.append(
            str(idx)
        )

    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

    print(
        "✅ Vector DB created successfully"
    )


# --------------------------------------------------
# AUTO-CREATE IF EMPTY
# --------------------------------------------------

try:

    if collection.count() == 0:

        print(
            "Creating vector DB..."
        )

        create_vector_db()

    else:

        print(
            f"Loaded DB with {collection.count()} items"
        )

except Exception as e:

    print(
        f"DB startup issue: {e}"
    )