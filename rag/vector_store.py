import chromadb

CHROMA_PATH="vector_db"

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_or_create_collection(
    name="shl_assessments"
)