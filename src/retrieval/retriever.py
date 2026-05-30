import chromadb

from chromadb.utils.embedding_functions import (
    SentenceTransformerEmbeddingFunction
)

from dotenv import load_dotenv

import os


# =====================================
# LOAD ENV
# =====================================

load_dotenv()

CHROMA_PATH = os.getenv(
    "CHROMA_PATH",
    "chroma_db"
)

COLLECTION_NAME = "zoning_docs"


# =====================================
# EMBEDDING FUNCTION
# =====================================

embedding_function = (
    SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
)


# =====================================
# CHROMA CLIENT
# =====================================

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_collection(

    name=COLLECTION_NAME,

    embedding_function=embedding_function
)


# =====================================
# MAIN RETRIEVAL FUNCTION
# =====================================

def retrieve_chunks(

    question: str,

    top_k: int = 5,

    threshold: float = 0.55

):

    results = collection.query(

        query_texts=[question],

        n_results=top_k
    )

    retrieved_chunks = []

    documents = results["documents"][0]

    metadatas = results["metadatas"][0]

    distances = results["distances"][0]

    ids = results["ids"][0]

    for idx in range(len(documents)):

        distance = distances[idx]

        # ---------------------------------
        # Distance filtering
        # ---------------------------------

        if distance > threshold:
            continue

        document = documents[idx]

        metadata = metadatas[idx]

        chunk_id = ids[idx]

        # ---------------------------------
        # Deterministic citation ID
        # ---------------------------------

        citation_id = (
            f"SOURCE_{len(retrieved_chunks)+1}"
        )

        retrieved_chunks.append({

            "citation_id":
            citation_id,

            "chunk_id":
            chunk_id,

            "text":
            document,

            "distance":
            distance,

            "source_file":
            metadata.get(
                "source_file"
            ),

            "section_title":
            metadata.get(
                "section_title"
            ),

            "last_amended":
            metadata.get(
                "last_amended"
            ),

            "start_line":
            metadata.get(
                "start_line"
            ),

            "end_line":
            metadata.get(
                "end_line"
            ),

            "has_cross_ref":
            metadata.get(
                "has_cross_ref"
            )
        })

    return retrieved_chunks


# =====================================
# TEST BLOCK
# =====================================

# if __name__ == "__main__":

#     question = (
#         "What are rear yard "
#         "requirements?"
#     )

#     chunks = retrieve_chunks(
#         question=question
#     )

#     print("\n=== RETRIEVED CHUNKS ===\n")

#     for chunk in chunks:

#         print(
#             f"{chunk['citation_id']}"
#         )

#         print(
#             f"Source: "
#             f"{chunk['source_file']}"
#         )

#         print(
#             f"Lines: "
#             f"{chunk['start_line']}"
#             f"-"
#             f"{chunk['end_line']}"
#         )

#         print(
#             f"Distance: "
#             f"{chunk['distance']}"
#         )

#         print(
#             chunk["text"][:300]
#         )

#         print("\n" + "="*60 + "\n")