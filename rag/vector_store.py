import json
import chromadb

from rag.embeddings import embedding_model


CHROMA_PATH = "vector_db"

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


def get_collection():

    return client.get_or_create_collection(
        name="shl_assessments"
    )


def create_vector_db():

    collection = get_collection()

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
        "Vector DB created successfully"
    )


if __name__=="__main__":
    create_vector_db()