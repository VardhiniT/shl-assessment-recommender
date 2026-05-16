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


# --------------------------------------------------
# VECTOR DB CREATION
# --------------------------------------------------

def create_vector_db(collection):

    with open(
        "data/processed_assessments.json",
        "r"
    ) as f:

        data = json.load(f)

    documents=[]
    embeddings=[]
    metadatas=[]
    ids=[]

    for idx,item in enumerate(data):

        search_text=item["search_text"]

        embedding=(
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
        "Vector DB created"
    )


# --------------------------------------------------
# LOAD / CREATE COLLECTION
# --------------------------------------------------

try:

    collection=client.get_collection(
        name="shl_assessments"
    )

    print(
        "Loaded existing collection"
    )

except:

    print(
        "Creating new collection"
    )

    collection=client.create_collection(
        name="shl_assessments"
    )

    create_vector_db(
        collection
    )