import os

from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# PERSIST MODEL CACHE
# Render's filesystem resets on restart — this path
# survives restarts and prevents re-downloading the
# ~90MB model every cold start
# --------------------------------------------------

os.environ["SENTENCE_TRANSFORMERS_HOME"] = (
    "/opt/render/project/src/.model_cache"
)


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

embedding_model = SentenceTransformer(MODEL_NAME)