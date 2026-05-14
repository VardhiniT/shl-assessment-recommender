import os
from sentence_transformers import SentenceTransformer

# This path is on the persistent disk — survives restarts
os.environ["SENTENCE_TRANSFORMERS_HOME"] = "/data/model_cache"
os.environ["HF_HOME"] = "/data/hf_cache"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
embedding_model = SentenceTransformer(MODEL_NAME)